# gRPC HotelReservation + Intel IPU Scripting

Usable scripting for running DeathStarBench's HotelReservation application with Intel's IPU emulator

## Installation

First ssh into your CloudLab master node with the -A option to cache public keys in your ssh-agent
#### Example
```bash
ssh -A edwinlim@ms0415.utah.cloudlab.us
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install foobar
```

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
