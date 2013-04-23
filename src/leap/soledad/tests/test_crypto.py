# -*- coding: utf-8 -*-
# test_crypto.py
# Copyright (C) 2013 LEAP
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
Tests for cryptographic related stuff.
"""


import os


from leap.common.testing.basetest import BaseLeapTest
from leap.soledad.backends.leap_backend import LeapDocument
from leap.soledad.tests import BaseSoledadTest
from leap.soledad.tests import (
    KEY_FINGERPRINT,
    PRIVATE_KEY,
)
from leap.soledad import KeyAlreadyExists
from leap.soledad.crypto import SoledadCrypto

try:
    import simplejson as json
except ImportError:
    import json  # noqa


class EncryptedSyncTestCase(BaseSoledadTest):
    """
    Tests that guarantee that data will always be encrypted when syncing.
    """

    def test_get_set_encrypted_json(self):
        """
        Test getting and setting encrypted content.
        """
        doc1 = LeapDocument(crypto=self._soledad._crypto)
        doc1.content = {'key': 'val'}
        doc2 = LeapDocument(doc_id=doc1.doc_id,
                            encrypted_json=doc1.get_encrypted_json(),
                            crypto=self._soledad._crypto)
        res1 = doc1.get_json()
        res2 = doc2.get_json()
        self.assertEqual(res1, res2, 'incorrect document encryption')

    def test_successful_symmetric_encryption(self):
        """
        Test for successful symmetric encryption.
        """
        doc1 = LeapDocument(crypto=self._soledad._crypto)
        doc1.content = {'key': 'val'}
        enc_json = json.loads(doc1.get_encrypted_json())['_encrypted_json']
        self.assertEqual(
            True,
            self._soledad._crypto.is_encrypted_sym(enc_json),
            "could not encrypt with passphrase.")


class RecoveryDocumentTestCase(BaseSoledadTest):

    def test_export_recovery_document_raw(self):
        rd = self._soledad.export_recovery_document(None)
        self.assertEqual(
            {
                'user': self._soledad._user,
                'symkey': self._soledad._symkey
            },
            json.loads(rd),
            "Could not export raw recovery document."
        )

    def test_export_recovery_document_crypt(self):
        rd = self._soledad.export_recovery_document('123456')
        self.assertEqual(True,
                         self._soledad._crypto.is_encrypted_sym(rd))
        data = {
            'user': self._soledad._user,
            'symkey': self._soledad._symkey,
        }
        raw_data = json.loads(str(self._soledad._crypto.decrypt(
            rd,
            passphrase='123456')))
        self.assertEqual(
            raw_data,
            data,
            "Could not export raw recovery document."
        )

    def test_import_recovery_document_raises_exception(self):
        rd = self._soledad.export_recovery_document(None)
        self.assertRaises(KeyAlreadyExists,
                          self._soledad.import_recovery_document, rd, None)

    def test_import_recovery_document_raw(self):
        rd = self._soledad.export_recovery_document(None)
        gnupg_home = self.gnupg_home = "%s/gnupg2" % self.tempdir
        s = self._soledad_instance(user='anotheruser@leap.se', prefix='/2')
        s._init_dirs()
        s._crypto = SoledadCrypto(gnupg_home)
        s.import_recovery_document(rd, None)
        self.assertEqual(self._soledad._user,
                         s._user, 'Failed setting user email.')
        self.assertEqual(self._soledad._symkey,
                         s._symkey,
                         'Failed settinng secret for symmetric encryption.')

    def test_import_recovery_document_crypt(self):
        rd = self._soledad.export_recovery_document('123456')
        gnupg_home = self.gnupg_home = "%s/gnupg2" % self.tempdir
        s = self._soledad_instance(user='anotheruser@leap.se', prefix='3')
        s._init_dirs()
        s._crypto = SoledadCrypto(gnupg_home)
        s.import_recovery_document(rd, '123456')
        self.assertEqual(self._soledad._user,
                         s._user, 'Failed setting user email.')
        self.assertEqual(self._soledad._symkey,
                         s._symkey,
                         'Failed settinng secret for symmetric encryption.')


class CryptoMethodsTestCase(BaseSoledadTest):

    def test__gen_symkey(self):
        sol = self._soledad_instance(user='user@leap.se', prefix='/3')
        sol._init_dirs()
        sol._crypto = SoledadCrypto("%s/3/gnupg" % self.tempdir)
        self.assertFalse(sol._has_symkey(), "Should not have a symkey at "
                                            "this point")
        sol._gen_symkey()
        self.assertTrue(sol._has_symkey(), "Could not generate symkey.")

    def test__has_keys(self):
        sol = self._soledad_instance(user='leap@leap.se', prefix='/5')
        sol._init_dirs()
        sol._crypto = SoledadCrypto("%s/5/gnupg" % self.tempdir)
        self.assertFalse(sol._has_keys())
        sol._gen_symkey()
        self.assertTrue(sol._has_keys())
