import importlib, asyncio
from pathlib import Path
from utils import exceptions, common

logger = common.getLogger('bot')

async def load_modules():
    modules = []
    module_dir = Path(__file__).parent
    module_prefix = module_dir.name
    for module in module_dir.iterdir():
        if module.is_dir() \
                and not module.name.startswith('_') \
                and module.joinpath('__init__.py').exists() \
                and not module.joinpath('.disable').exists():
            logger.info(f'加载{module.name}模块')
            run = importlib.import_module(f'{module_prefix}.{module.name}')
            modules.append(run.main())
    if not modules:
        logger.warning('无可用模块')
        return
    await asyncio.gather(*modules)
