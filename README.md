## Steganography

How to hide a message:

```Bash
$ python lsb.py -p ~/path/to/image.png \
    -m "Hidden message!" \
    -o ~/path/to/modified_image.png
```

How to recover a message:

```Bash
$ python lsb.py -p ~/path/to/modified_image.png
```
