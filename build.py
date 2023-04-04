#!/usr/bin/env python3

# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import importlib
import os
import sys
import tarfile

from urllib.error import HTTPError

# include libdbr in module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))

from libdbr        import config
from libdbr        import modules
from libdbr        import paths
from libdbr        import tasks
from libdbr.logger import getLogger


## Download packages from remote sources.
def taskDownloadPackages():
  print("\ndownloading packages ...")

  try:
    wget = importlib.import_module("wget")
  except ModuleNotFoundError:
    modules.installModule("wget")
    wget = importlib.import_module("wget")

  wx_pre = "https://github.com/wxWidgets/wxWidgets/releases/download"
  # ~ svg_pre = "https://sourceforge.net/projects/wxsvg/files/wxsvg"
  svg_pre = "https://downloads.sourceforge.net/project/wxsvg/wxsvg"
  py_pre = "https://github.com/wxWidgets/Phoenix/releases/download/wxPython"

  for pkg_ver in config.getValue("wx_versions").split(";"):
    pkg_name = "wxWidgets-{}.tar.bz2".format(pkg_ver)
    pkg_path = paths.join(dir_root, pkg_name)
    pkg_url = "{}/v{}/{}".format(wx_pre, pkg_ver, pkg_name)
    print("downloading file from '{}'".format(pkg_url))
    if os.path.exists(pkg_path):
      logger.info("skipping present package '{}'".format(pkg_name))
    else:
      try:
        wget.download(pkg_url)
      except KeyboardInterrupt:
        print() # flush stdout buffer
        logger.info("transaction cancelled by user")
        sys.exit(0)
      except HTTPError as e:
        print() # flush stdout buffer
        logger.error("download failed: {}".format(e))
        sys.exit(1)
  for pkg_ver in config.getValue("wx_svg_versions").split(";"):
    pkg_name = "wxsvg-{}.tar.bz2".format(pkg_ver)
    pkg_path = paths.join(dir_root, pkg_name)
    # ~ pkg_url = "{}/{}/{}/download".format(svg_pre, pkg_ver, pkg_name)
    pkg_url = "{}/{}/{}".format(svg_pre, pkg_ver, pkg_name)
    print("\ndownloading file from '{}'".format(pkg_url))
    if os.path.exists(pkg_path):
      logger.info("skipping present package '{}'".format(pkg_name))
    else:
      try:
        wget.download(pkg_url)
      except KeyboardInterrupt:
        print() # flush stdout buffer
        logger.info("transaction cancelled by user")
        sys.exit(0)
      except HTTPError as e:
        print() # flush stdout buffer
        logger.error("download failed: {}".format(e))
        sys.exit(1)
  for pkg_ver in config.getValue("wx_py_versions").split(";"):
    pkg_name = "wxPython-{}.tar.gz".format(pkg_ver)
    pkg_path = paths.join(dir_root, pkg_name)
    pkg_url = "{}-{}/{}".format(py_pre, pkg_ver, pkg_name)
    print("\ndownloading file from '{}'".format(pkg_url))
    if os.path.exists(pkg_path):
      logger.info("skipping present package '{}'".format(pkg_name))
    else:
      try:
        wget.download(pkg_url)
        print() # flush stdout buffer
      except KeyboardInterrupt:
        print() # flush stdout buffer
        logger.info("transaction cancelled by user")
        sys.exit(0)
      except HTTPError as e:
        print() # flush stdout buffer
        logger.error("download failed: {}".format(e))
        sys.exit(1)

def addTask(name, action, desc):
  tasks.add(name, action)
  task_list[name] = desc

def initTasks():
  addTask("download", taskDownloadPackages, "Download source packages.")

## Main insertion function.
def main():
  global dir_root, task_list, logger

  logger = getLogger(".".join(os.path.basename(__file__).split(".")[0:-1]))

  dir_root = os.path.dirname(os.path.realpath(sys.argv[0]))
  file_config = paths.join(dir_root, "build.conf")
  config.setFile(file_config)
  config.load()

  task_list = {}
  initTasks()

  # TODO: add print usage function
  if len(sys.argv) < 2:
    logger.error("missing command argument ({})".format(",".join(task_list)))
    sys.exit(1)
  t = sys.argv[1]
  if t not in task_list:
    logger.error("unknown task '{}'".format(t))
    sys.exit(1)

  tasks.run(t)

if __name__ == "__main__":
  main()
