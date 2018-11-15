# A Magento 2 module generator library
# Copyright (C) 2018 Derrick Heesbeen
#
# This file is part of Mage2Gen.
#
# Mage2Gen is free software: you can redistribute it and/or modify
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
import os
from .. import Module,Phpclass, Phpmethod, Xmlnode, Snippet, SnippetParam, GraphQlSchema, GraphQlObjectType
from ..utils import upperfirst, lowerfirst


class GraphQlSnippet(Snippet):
    snippet_label = 'GraphQl'

    description = """
	
	"""

    GRAPHQL_TYPE_CHOISES = [
        ('Query', 'Query'),
        ('Mutation', 'Mutation')
    ]

    def add(self, base_type, identifier, extra_params=None):
        identifier = lowerfirst(identifier)
        item_identifier = upperfirst(identifier)
        resolver_graphqlformat = '{}\\\{}\\\Model\\\Resolver\\\{}'.format(self._module.package, self._module.name, item_identifier)

        base_type_schema = GraphQlSchema()
        base_type_schema.add_objecttype(
            GraphQlObjectType(
                base_type,
                body='{identifier} : {item_identifier} @resolver(class: "{resolver}") @doc(description: "The {item_identifier} query")'.format(
                    identifier=identifier,
                    item_identifier=item_identifier,
                    resolver=resolver_graphqlformat
                )
            )
        )
        base_type_schema.add_objecttype(
            GraphQlObjectType(
                item_identifier,
                body='id : Int @doc(description: "Item Identifier")'
            )
        )
        self.add_graphqlschema('etc/schema.graphqls', base_type_schema)

        resolver = Phpclass(
            'Model\\Resolver\\{}'.format(item_identifier),
            implements=['ResolverInterface'],
            dependencies=[
                'Magento\\Framework\\Exception\\NoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Config\\Element\\Field',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlInputException',
                'Magento\\Framework\\GraphQl\\Exception\\GraphQlNoSuchEntityException',
                'Magento\\Framework\\GraphQl\\Query\\ResolverInterface',
                'Magento\\Framework\\GraphQl\\Schema\\Type\\ResolveInfo',
            ],
            attributes=[
                'private ${}DataProvider;'.format(identifier)
            ]
        )

        resolver.add_method(
            Phpmethod(
                '__construct',
                params=[
                    'DataProvider\\{} ${}DataProvider'.format(item_identifier, identifier)
                ],
                body="$this->{0}DataProvider = ${0}DataProvider;".format(identifier),
                docstring=[
                    '@param DataProvider\\{} ${}Repository'.format(item_identifier, identifier)
                ]
            )
        )

        resolver.add_method(
            Phpmethod(
                'resolve',
                params=[
                    'Field $field',
                    '$context',
                    'ResolveInfo $info',
                    'array $value = null',
                    'array $args = null'
                ],
                body="""${0}Data = $this->{0}DataProvider->get{1}();
return ${0}Data;""".format(identifier, item_identifier),
                docstring=[
                    '@inheritdoc'
                ]
            )
        )

        self.add_class(resolver)

        data_provider = Phpclass(
            'Model\\Resolver\\DataProvider\\{}'.format(item_identifier),
            dependencies=[],
            attributes=[]
        )

        data_provider.add_method(
            Phpmethod(
                '__construct',
                params=[],
                body="",
                docstring=[]
            )
        )

        data_provider.add_method(
            Phpmethod(
                'get{}'.format(item_identifier),
                params=[],
                body="return 'proviced data';",
                docstring=[]
            )
        )

        self.add_class(data_provider)

        sequence_modules = [
            Xmlnode('module', attributes={'name': 'Magento_GraphQl'})
        ]
        etc_module = Xmlnode('config', attributes={
            'xsi:noNamespaceSchemaLocation': "urn:magento:framework:Module/etc/module.xsd"}, nodes=[
            Xmlnode('module', attributes={'name': self.module_name}, nodes=[
                Xmlnode('sequence', attributes={}, nodes=sequence_modules)
            ])
        ])
        self.add_xml('etc/module.xml', etc_module)

    @classmethod
    def params(cls):
        return [
            SnippetParam(name='base_type', choises=cls.GRAPHQL_TYPE_CHOISES, default='Query'),
            SnippetParam(
                name='identifier', required=True,
                description='Example: storeConfig',
                regex_validator=r'^[a-zA-Z\d\-_\s]+$',
                error_message='Only alphanumeric'
            )
        ]


