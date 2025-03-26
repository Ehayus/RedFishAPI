# SPDX-License-Identifier: BSD-3-Clause
#
# Copyright 2022 Raritan Inc. All rights reserved.

# The generic classes UniversalResource and UniversalCollection allow
# access to resources for which Sushy does not yet provide specialized classes.

import logging
from sushy.resources import base

LOG = logging.getLogger(__name__)

class UniversalResource(base.ResourceBase):
    fields = None

    def __init__(self, connector, identity, redfish_version = None,
                 registries = None, fields = {}):
        """A class representing a generic resource, used for resources
           currently not explicitly supported

        :param connector: A Connector instance
        :param identity: The identity of the Resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        """
        for key, field in fields.items():
            setattr(self.__class__, key, field)

        super(UniversalResource, self).__init__(
            connector, identity, redfish_version, registries)

class UniversalCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return UniversalResource

    def __init__(self, connector, path, redfish_version = None, registries = None, fields = {}):
        """A class representing a universal collection

        :param connector: A Connector instance
        :param path: The canonical path to the Collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        :param registries: Dict of Redfish Message Registry objects to be
            used in any resource that needs registries to parse messages
        :param root: Sushy root object. Empty for Sushy root itself.
        """
        for key, field in fields.items():
            setattr(self.__class__, key, field)

        super(UniversalCollection, self).__init__(
            connector, path, redfish_version=redfish_version,
            registries=registries)


    def get_member(self, identity, fields = {}):
        return UniversalResource(self._conn, identity, self.redfish_version, self.registries, fields)

    def get_members(self, fields = {}):
        return [self.get_member(id_, fields) for id_ in self.members_identities]

def get_resource(sushy, identity, fields = {}):
    return UniversalResource(sushy._conn, identity,
                             redfish_version=sushy.redfish_version,
                             registries=sushy.lazy_registries,
                             fields = fields)

def get_collection(sushy, identity, fields = {}):
    return UniversalCollection(sushy._conn, identity,
                               redfish_version=sushy.redfish_version,
                               registries=sushy.lazy_registries,
                               fields = fields)
