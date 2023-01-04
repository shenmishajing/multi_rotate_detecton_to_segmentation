from types import MethodType
from typing import Optional

from lightning.pytorch import Trainer as _Trainer
from lightning.pytorch.utilities.argparse import _defaults_from_env_vars

from ..loop import KFoldLoop


def _update_learning_rates(self, *args, **kwargs) -> None:
    automatic_optimization = self.trainer.lightning_module.automatic_optimization
    self.trainer.lightning_module.automatic_optimization |= (
        self.trainer.lightning_module.automatic_lr_schedule
    )
    self._origin_update_learning_rates(*args, **kwargs)
    self.trainer.lightning_module.automatic_optimization = automatic_optimization


class Trainer(_Trainer):
    @_defaults_from_env_vars
    def __init__(self, num_folds: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fit_loop.epoch_loop._origin_update_learning_rates = (
            self.fit_loop.epoch_loop._update_learning_rates
        )
        self.fit_loop.epoch_loop._update_learning_rates = MethodType(
            _update_learning_rates, self.fit_loop.epoch_loop
        )
        # add kfold cross validation support
        self.num_folds = num_folds
        if self.num_folds is not None and self.num_folds > 1:
            self.fit_loop = KFoldLoop(self.num_folds, self.fit_loop)
