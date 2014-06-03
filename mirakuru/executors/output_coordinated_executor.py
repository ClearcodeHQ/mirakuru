# Copyright (C) 2014 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of mirakuru.

# mirakuru is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mirakuru is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with mirakuru.  If not, see <http://www.gnu.org/licenses/>.

import re
from mirakuru.executors import SimpleExecutor


class OutputCoordinatedExecutor(SimpleExecutor):

    def __init__(self, command, banner, shell=False, timeout=None):
        SimpleExecutor.__init__(self, command, shell, timeout)
        self._banner = re.compile(banner)

    def start(self):
        SimpleExecutor.start(self)
        self._wait_for_output()

    def _wait_for_output(self):
        while self.check_timeout():
            if self._banner.match(self.output().readline()):
                break
