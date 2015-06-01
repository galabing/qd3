import logging
import os

def configLogging(level=logging.INFO):
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)

# Runs command and maybe checks success.
def run(cmd, check=True, dry_run=False):
  logging.info('running command: %s' % cmd)
  if dry_run:
    return 0
  result = os.system(cmd)
  if check:
    assert result == 0
  return result

