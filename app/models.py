import sys
from app import utils
if utils.CIS:
    sys.path.append("/mounts/work/philipp/simalign-demo/simalign")
else:
    sys.path.append("/Users/philipp/Dropbox/PhD/projects/simalign")
# import simalign


class PLM(object):
    """docstring for PLM"""

    def __init__(self):
        super(PLM, self).__init__()
        utils.LOG.info("Loading alignment models...")
        self.aligners = {}
        self.aligners["bert"] = simalign.SentenceAligner(model="bert", token_type="bpe",
                                                         cache_dir="/mounts/work/philipp/simalign-demo/cachedir")
        # self.aligners["xlmr"] = simalign.SentenceAligner(model="xlmr", token_type="bpe")
        utils.LOG.info("Loading alignment models finished.")
