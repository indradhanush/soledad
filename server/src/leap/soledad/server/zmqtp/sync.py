# -*- coding: utf-8 -*-
# sync.py
# Copyright (C) 2014 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""
Extends default U1DB components and adds to them as and where necessary.
"""
from u1db import sync


class ZMQSyncExchange(sync.SyncExchange):
    """
    Extends u1db.remote.sync.SyncExchange
    """
    def get_docs(self, changed_doc_ids, check_for_conflicts=True,
                 include_deleted=False):
        """
        Helper utility to provide access to private instance
        variable self._db.
        """
        return self._db.get_docs(changed_doc_ids, check_for_conflicts,
                                 include_deleted)

    def get_generation_info(self):
        """
        Wrapper to access private method _get_generation_info of private
        attribute _db.

        :return: A tuple containing the docs by generation, the updated
                 target generation and the transaction id.
        :rtype: tuple
        """
        return self._db._get_generation_info()
