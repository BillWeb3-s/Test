import asyncio
import logging
from src.config import AppConfig
from src.monitor import TGClient, ChannelMonitor
from src.utils import setup_logger
from src.coingecko import TokenInfoService, ContractAddressEnricher


async def main():
    """Main entry point for the application"""
    
    setup_logger(
        name=None,  
        level=logging.INFO,
        log_dir="logs",
        log_filename="app.log"
    )
    logger = logging.getLogger(__name__)

    monitor = None
    token_service = None
    try:
        
        logger.info("Loading configuration...")
        config = AppConfig.from_env()

        
        logger.info("Starting TokenInfoService...")
        token_service = TokenInfoService(
            cache_file="data/coingecko_cache.json",
            update_interval=600  
        )
        await token_service.start()

        
        logger.info("Initializing ContractAddressEnricher...")
        enricher = ContractAddressEnricher(token_service)

        
        logger.info("Initializing Telegram client...")
        tg_client = TGClient(config.telegram)

        
        logger.info("Starting channel monitor...")
        monitor = ChannelMonitor(
            tg_client,
            config.monitor,
            config.price,
            config.blockchain,
            config.wallet,
            config.lark,
            enricher
        )
        await monitor.run()

    except KeyboardInterrupt:
        logger.info("Received stop signal")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        if monitor:
            await monitor.stop()
        if token_service:
            await token_service.stop()
        logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
