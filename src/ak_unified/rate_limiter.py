"""
Rate limiter for controlling API request frequency across different data sources.
Uses aiolimiter to implement token bucket rate limiting.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Optional, Union
from aiolimiter import AsyncLimiter
from .config import settings
from .logging import logger


class RateLimiterManager:
    """Manages rate limiters for different data sources and vendors."""
    
    def __init__(self):
        # Maintain limiters per event loop to avoid cross-loop reuse
        self._limiters_by_loop: Dict[int, Dict[str, AsyncLimiter]] = {}
        self._daily_by_loop: Dict[int, Dict[str, AsyncLimiter]] = {}
        self._initialized = False
        
    async def _ensure_initialized(self):
        """Initialize rate limiters if not already done."""
        # Initialization is now per loop
        loop = asyncio.get_running_loop()
        loop_id = id(loop)
        if loop_id in self._limiters_by_loop:
            return
            
        # Initialize Alpha Vantage limiters
        if settings.RATE_LIMIT_ENABLED:
            # Per-minute limiter (5 requests per minute for free tier)
            self._limiters_by_loop[loop_id] = {
                'alphavantage': AsyncLimiter(settings.AV_RATE_LIMIT_PER_MIN, 60.0)
            }
            
            # Daily limiter (500 requests per day for free tier)
            self._daily_by_loop[loop_id] = {
                'alphavantage': AsyncLimiter(settings.AV_RATE_LIMIT_PER_DAY, 86400.0)
            }
            
            # Initialize AkShare vendor limiters
            vendor_limits = {
                # Relax defaults for local/dev verification
                'eastmoney': max(120, settings.AKSHARE_EASTMONEY_RATE_LIMIT),
                'sina': max(120, settings.AKSHARE_SINA_RATE_LIMIT),
                'tencent': max(120, settings.AKSHARE_TENCENT_RATE_LIMIT),
                'ths': max(60, settings.AKSHARE_THS_RATE_LIMIT),
                'tdx': max(120, settings.AKSHARE_TDX_RATE_LIMIT),
                'baidu': max(60, settings.AKSHARE_BAIDU_RATE_LIMIT),
                'netease': max(120, settings.AKSHARE_NETEASE_RATE_LIMIT),
                'hexun': max(60, settings.AKSHARE_HEXUN_RATE_LIMIT),
                'csindex': max(60, settings.AKSHARE_CSINDEX_RATE_LIMIT),
                'jisilu': max(30, settings.AKSHARE_JISILU_RATE_LIMIT),
            }
            
            for vendor, limit in vendor_limits.items():
                self._limiters_by_loop[loop_id][f'akshare_{vendor}'] = AsyncLimiter(limit, 60.0)
            
            # Default AkShare limiter
            self._limiters_by_loop[loop_id]['akshare_default'] = AsyncLimiter(max(120, settings.AKSHARE_DEFAULT_RATE_LIMIT), 60.0)
            
            # Snowball rate limiters
            self._limiters_by_loop[loop_id]['snowball_default'] = AsyncLimiter(max(120, settings.SNOWBALL_DEFAULT_RATE_LIMIT), 60.0)
            
            # EasyTrader rate limiters
            self._limiters_by_loop[loop_id]['easytrader_default'] = AsyncLimiter(max(60, settings.EASYTRADER_DEFAULT_RATE_LIMIT), 60.0)
            self._limiters_by_loop[loop_id]['easytrader_login'] = AsyncLimiter(max(10, settings.EASYTRADER_LOGIN_RATE_LIMIT), 60.0)
            
            logger.debug(f"Rate limiter pool created with {len(self._limiters_by_loop[loop_id])} limiters for loop {loop_id}")
        else:
            logger.info("Rate limiting disabled")
            
        self._initialized = True
    
    async def acquire(self, source: str, vendor: Optional[str] = None) -> None:
        """
        Acquire permission to make a request.
        
        Args:
            source: Data source ('alphavantage', 'akshare', etc.)
            vendor: Vendor name for AkShare functions (e.g., 'eastmoney', 'sina')
        """
        if not settings.RATE_LIMIT_ENABLED:
            return
            
        await self._ensure_initialized()
        
        loop_id = id(asyncio.get_running_loop())
        limiter_key = self._get_limiter_key(source, vendor)
        limiter = self._limiters_by_loop.get(loop_id, {}).get(limiter_key)
        
        if limiter:
            try:
                loop = asyncio.get_running_loop()
                start = loop.time()
                await limiter.acquire()
                waited = (loop.time() - start)
                # Only log when we actually throttled (waited > 20ms)
                if waited > 0.02:
                    logger.warning(f"Rate limited {limiter_key}: waited {waited*1000:.1f}ms")
                else:
                    logger.debug(f"Rate limit acquired for {limiter_key}")
            except Exception as e:
                logger.warning(f"Failed to acquire rate limit for {limiter_key}: {e}")
        else:
            logger.warning(f"No rate limiter found for {limiter_key}")
    
    async def acquire_daily(self, source: str) -> None:
        """
        Acquire permission for daily limit (mainly for Alpha Vantage).
        
        Args:
            source: Data source ('alphavantage')
        """
        if not settings.RATE_LIMIT_ENABLED:
            return
            
        await self._ensure_initialized()
        
        loop_id = id(asyncio.get_running_loop())
        daily_limiter = self._daily_by_loop.get(loop_id, {}).get(source)
        if daily_limiter:
            try:
                await daily_limiter.acquire()
                logger.debug(f"Daily rate limit acquired for {source}")
            except Exception as e:
                logger.warning(f"Failed to acquire daily rate limit for {source}: {e}")
    
    def _get_limiter_key(self, source: str, vendor: Optional[str] = None) -> str:
        """Get the appropriate limiter key based on source and vendor."""
        if source == 'alphavantage':
            return 'alphavantage'
        elif source == 'akshare':
            if vendor and vendor != 'unknown':
                return f'akshare_{vendor}'
            else:
                return 'akshare_default'
        else:
            return f'{source}_default'
    
    async def get_limiter_status(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Get current status of all limiters."""
        await self._ensure_initialized()
        
        status = {}
        for key, limiter in self._limiters.items():
            status[key] = {
                'max_rate': limiter.max_rate,
                'time_period': limiter.time_period,
                'rate_per_sec': getattr(limiter, '_rate_per_sec', None),
                'level': getattr(limiter, '_level', None),
                'has_capacity': limiter.has_capacity()
            }
        
        for key, limiter in self._daily_limiters.items():
            status[f'{key}_daily'] = {
                'max_rate': limiter.max_rate,
                'time_period': limiter.time_period,
                'rate_per_sec': getattr(limiter, '_rate_per_sec', None),
                'level': getattr(limiter, '_level', None),
                'has_capacity': limiter.has_capacity()
            }
            
        return status


# Global rate limiter manager instance
rate_limiter = RateLimiterManager()


async def acquire_rate_limit(source: str, vendor: Optional[str] = None) -> None:
    """
    Convenience function to acquire rate limit permission.
    
    Args:
        source: Data source ('alphavantage', 'akshare', etc.)
        vendor: Vendor name for AkShare functions
    """
    await rate_limiter.acquire(source, vendor)


async def acquire_daily_rate_limit(source: str) -> None:
    """
    Convenience function to acquire daily rate limit permission.
    
    Args:
        source: Data source ('alphavantage')
    """
    await rate_limiter.acquire_daily(source)


async def get_rate_limit_status() -> Dict[str, Dict[str, Union[int, float]]]:
    """Get current rate limiter status."""
    return await rate_limiter.get_limiter_status()