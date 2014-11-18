<Shortcut Id="{{ element.id }}" Name="{{ element.shortcut_name }}" Description="{{ element.shortcut_name }}"
          Advertise="no" Target="[INSTALLDIR]bin\{{ element.executable_name }}.exe" WorkingDirectory="INSTALLDIR"
          {% if element.icon_id %}Icon="{{ element.icon_id }}"{% endif %}/>