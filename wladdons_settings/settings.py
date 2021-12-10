# Default settings for retrieving Email settings for the add-ons server
# !!! Do not edit the main keys once this got merged !!!
# The values for 'display' and 'description can be edited after merging, they 
# will be updated if users enters the respective profile tab.

ADDONNOTICETYPES = {
    'addon_deleted': {'display': 'Your Add-On was deleted',
                      'description': 'an add-on made by you was deleted',
                      },
    'addon_transifex_issues': {'display': 'Translation issues',
                               'description': 'there are translation issues with your add-on',
                               }
}
