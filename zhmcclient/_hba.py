# Copyright 2016 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A :term:`HBA` (Host Bus Adapter) is a logical entity that provides a
:term:`Partition` with access to external storage area networks (SANs) through
an :term:`FCP Adapter`. More specifically, an HBA connects a Partition with an
:term:`Adapter Port` on an FCP Adapter.

HBA resources are contained in Partition resources.

HBAs only exist in :term:`CPCs <CPC>` that are in DPM mode.
"""

from __future__ import absolute_import

from ._manager import BaseManager
from ._resource import BaseResource

__all__ = ['HbaManager', 'Hba']


class HbaManager(BaseManager):
    """
    Manager providing access to the :term:`HBAs <HBA>` in a particular
    :term:`Partition`.

    Derived from :class:`~zhmcclient.BaseManager`; see there for common methods
    and attributes.

    Objects of this class are not directly created by the user; they are
    accessible via the following instance variable of a
    :class:`~zhmcclient.Partition` object (in DPM mode):

    * :attr:`~zhmcclient.Partition.hbas`
    """

    def __init__(self, partition):
        # This function should not go into the docs.
        # Parameters:
        #   partition (:class:`~zhmcclient.Partition`):
        #     Partition defining the scope for this manager.

        super(HbaManager, self).__init__(
            resource_class=Hba,
            parent=partition,
            uri_prop='element-uri',
            name_prop='name',
            query_props=[])

    @property
    def partition(self):
        """
        :class:`~zhmcclient.Partition`: :term:`Partition` defining the scope
        for this manager.
        """
        return self._parent

    def list(self, full_properties=False, filter_args=None):
        """
        List the HBAs in this Partition.

        Authorization requirements:

        * Object-access permission to this Partition.

        Parameters:

          full_properties (bool):
            Controls whether the full set of resource properties should be
            retrieved, vs. only the short set as returned by the list
            operation.

          filter_args (dict):
            Filter arguments that narrow the list of returned resources to
            those that match the specified filter arguments. For details, see
            :ref:`Filtering`.

            `None` causes no filtering to happen, i.e. all resources are
            returned.

        Returns:

          : A list of :class:`~zhmcclient.Hba` objects.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        resource_obj_list = []
        uris = self.partition.get_property('hba-uris')
        if uris:
            for uri in uris:

                resource_obj = self.resource_class(
                    manager=self,
                    uri=uri,
                    name=None,
                    properties=None)

                if self._matches_filters(resource_obj, filter_args):
                    resource_obj_list.append(resource_obj)
                    if full_properties:
                        resource_obj.pull_full_properties()
        return resource_obj_list

    def create(self, properties):
        """
        Create and configure an HBA in this Partition.

        Authorization requirements:

        * Object-access permission to this Partition.
        * Object-access permission to the backing Adapter for the new HBA.
        * Task permission to the "Partition Details" task.

        Parameters:

          properties (dict): Initial property values.
            Allowable properties are defined in section 'Request body contents'
            in section 'Create HBA' in the :term:`HMC API` book.

            The underlying :term:`FCP port` for the new HBA is assigned via the
            "adapter-port-uri" property, which specifies the Port on the
            backing Adapter.

        Returns:

          Hba:
            The resource object for the new HBA.
            The object will have its 'element-uri' property set as returned by
            the HMC, and will also have the input properties set.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        result = self.session.post(self.partition.uri + '/hbas',
                                   body=properties)
        # There should not be overlaps, but just in case there are, the
        # returned props should overwrite the input props:
        props = properties.copy()
        props.update(result)
        return Hba(self, props['element-uri'], None, props)


class Hba(BaseResource):
    """
    Representation of an :term:`HBA`.

    Derived from :class:`~zhmcclient.BaseResource`; see there for common
    methods and attributes.

    For the properties of an HBA resource, see section
    'Data model - HBA Element Object' in section 'Partition object' in the
    :term:`HMC API` book.

    Objects of this class are not directly created by the user; they are
    returned from creation or list functions on their manager object
    (in this case, :class:`~zhmcclient.HbaManager`).
    """

    def __init__(self, manager, uri, name=None, properties=None):
        # This function should not go into the docs.
        # Parameters:
        #   manager (:class:`~zhmcclient.HbaManager`):
        #     Manager object for this resource object.
        #   uri (string):
        #     Canonical URI path of the resource.
        #   name (string):
        #     Name of the resource.
        #   properties (dict):
        #     Properties to be set for this resource object. May be `None` or
        #     empty.
        if not isinstance(manager, HbaManager):
            raise AssertionError("Hba init: Expected manager type %s, got %s" %
                                 (HbaManager, type(manager)))
        super(Hba, self).__init__(manager, uri, name, properties)

    def delete(self):
        """
        Delete this HBA.

        Authorization requirements:

        * Object-access permission to the Partition containing this HBA.
        * Task permission to the "Partition Details" task.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        self.manager.session.delete(self._uri)

    def update_properties(self, properties):
        """
        Update writeable properties of this HBA.

        Authorization requirements:

        * Object-access permission to the Partition containing this HBA.
        * **TBD: Verify:** Object-access permission to the backing Adapter for
          this HBA.
        * Task permission to the "Partition Details" task.

        Parameters:

          properties (dict): New values for the properties to be updated.
            Properties not to be updated are omitted.
            Allowable properties are the properties with qualifier (w) in
            section 'Data model - HBA Element Object' in the
            :term:`HMC API` book.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        self.manager.session.post(self._uri, body=properties)

    def reassign_port(self, port):
        """
        Reassign this HBA to a new underlying :term:`FCP port`.

        This method performs the HMC operation "Reassign Storage Adapter Port".

        Authorization requirements:

        * Object-access permission to the Partition containing this HBA.
        * Object-access permission to the Adapter with the new Port.
        * Task permission to the "Partition Details" task.

        Parameters:

          port (:class:`~zhmcclient.Port`): :term:`FCP port` to be used.

        Raises:

          :exc:`~zhmcclient.HTTPError`: See the HTTP status and reason codes of
            operation "Reassign Storage Adapter Port" in the :term:`HMC API`
            book.
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        body = {'adapter-port-uri': port.uri}
        self.manager.session.post(self._uri +
                                  '/operations/reassign-storage-adapter-port',
                                  body=body)
