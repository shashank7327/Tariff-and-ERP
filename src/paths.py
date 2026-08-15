"""Where things live.

Everything resolves from the repository root, so the scripts run from anywhere.
Point ALU_DATA at another directory if you keep the source data outside the repo.
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('ALU_DATA', REPO / 'data'))
TEX = REPO / 'tex'
BUILD = REPO / 'build'

ASI_CSV = DATA / 'ASI_National.csv'
ECTR_CSV = DATA / 'data_nic_ectr.csv'

BUILD.mkdir(exist_ok=True)
