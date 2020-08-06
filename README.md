# Open World Builder
An application in order to create and manage worldbuilding, characters and storylines.

- Geography with locations (link to characters and events)
- Characters (character details, link to other characters and events)
- Events (link to characters, timelines and locations)
- character arcs (link to characters and events)
- timelines

The desktop frontend used for Linux and Windows

## Release Notes
### Release 0

## Roadmap

## Development

### install dependencies
```
pip3 install --upgrade -r requirements.txt 
```


## Running the tests


### Break down into end to end tests


### And coding style tests


## Deployment


## Built With PyInstaller 
(deploy cross platform desktop gui)

### install
```
pip3 install --user pyinstaller         # (dev) to create an installer for desktop OS like windows, ubuntu, ios
```

### Create distribution
#### Windows 10 (64bit)
directory
```
python -m PyInstaller cli.py --icon="gui\warhammer_icon.ico" --name WAM-Win10-64-major-minor-patch-ext
```

#### Ubuntu 18 (64bit)
appimage
```
pyinstaller -F cli.py --name WAM-Ubuntu18-64-major-minor-patch-ext
```
directory
```
pyinstaller cli.py --name WAM-Ubuntu18-64-major-minor-patch-ext
```

### create a distribution from spec file with 
```
python -m PyInstaller WAM.spec
```
<!-- python -m PyInstaller WAM_OF.spec -->


## Contributing



## Versioning



## Authors

**Michael-Yongshi** 

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

Licensed under GPL-3.0-or-later, see LICENSE file for details.

Copyright © 2020 Michael-Yongshi.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.


## Acknowledgments

