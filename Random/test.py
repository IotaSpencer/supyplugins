###
# Copyright (c) 2017, Ken Spencer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from supybot.test import *


class RandomTestCase(PluginTestCase):
    plugins = ('Random',)

    def testRandInt(self):
        self.assertNotError("randint 1,10000000000000000000000000000000000000000000000000000000000000000000000000000000") # allow positive and big numbers
        self.assertNotError("randint -100000000000000000000000000000000000000000000000000000000,1000000000000000000000000000000000000000000000000000000000") # allow negative numbers
        self.assertNotError("randint -100000000000000000000000000000000000000000000000000,-1")
        self.assertError("randint a,z") # disallow letters
        self.assertError("randint A,Z") # disallow letters
        self.assertNotError("randint") # random int between 1 to 1000
    def testRandUAlpha(self):
        self.assertNotError("randualpha A,Z")
    def testRandLAlpha(self):
        self.assertNotError("randlalpha a,z")

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
