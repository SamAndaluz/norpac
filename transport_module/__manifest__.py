# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Freight Transport Management and Delivery Routes in Odoo',
    'version': '15.0.0.1',
    'category': 'Sales',
    'summary': 'Apps for Freight Delivery management Transport Delivery Routes Vehicles Transport Vehicles Freight TMS freight transportation logistic transport management delivery transport picking transport logistics System Transport Routes Delivery',
    'description'	: """
        Features of this Module includes::
        odoo transport module
        odoo Managing transport details enter transport details with sales order linked transport details with the picking Transport management with delivery order
        odoo Transport Management and Delivery Routes Picking Transport Details
        odoo Transport Route Locations Freight Management Transportation logistics management Route optimization
        odoo Transport Routes Delivery Routes management logestic transport management Transporters Details
        odoo Vehicles Transport Vehicles Freight Transport module
        odoo Freight Management Freight transport
    """,
    'author': 'BrowseInfo',
    'price': 45.00,
    'currency': "EUR",
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'sale', 'sale_management', 'stock', 'sale_stock' , 'account', 'fleet'],

    'data': [
            'security/ir.model.access.csv',
            'views/view_of_no_of_parcel_wizard.xml',
            'report/inherited_delivery_slip_report.xml',
            'wizard/view_reschedule_entry.xml',
            'views/transport.xml',
            'views/transport_entry_report.xml',
            'views/transport_report.xml',
            'views/view_fleet_vehicle.xml',
            'report/transport_report_menu.xml',
            'report/transport_document.xml',
            'data/seq.xml',
            ],
    'demo': [],
    'test': [
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url':'https://youtu.be/cph51j6S7ys',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


