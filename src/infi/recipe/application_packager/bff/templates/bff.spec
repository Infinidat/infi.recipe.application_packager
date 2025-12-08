Package Name: {{ package }}
Package VRMF: {{ version }}
Update: N
Fileset
  Fileset Name: {{ package }}.rte
  Fileset VRMF: {{ version }}
  Fileset Description: {{ description }}
  USRLIBLPPFiles
    Pre-installation Script: {{ temproot }}/preinstall
    Post-installation Script: {{ temproot }}/postinstall
    Pre-deinstall Script: {{ temproot }}/preremove
    Unpre-installation Script: {{ temproot }}/postremove
  EOUSRLIBLPPFiles
  Bosboot required: N
  License agreement acceptance required: N
  Include license files in this package: N
  Requisites:
  USRFiles
{% for directory in directories %}
    {{ directory }}
{% endfor %}
{% for file in files %}
    {{ file }}
{% endfor %}
  EOUSRFiles
  ROOT Part: N
  ROOTFiles
  EOROOTFiles
  Relocatable: N
EOFileset
