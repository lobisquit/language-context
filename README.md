# language-context

This package adds support for the ConTeXt markup language in Atom, with syntax highlighting.

It was originally ported from an old [TextMate bundle](<https://github.com/pgundlach/context.tmbundle>), but the current version is converted from ConTeXt LMTX interface XMLs with the help of the included Python script and enhanced with information from the wiki.

See [here](https://wiki.contextgarden.net/) for details about ConTeXt.

---

## Install
Run the following command, or search `language-context` in *Atom settings -> Install*.

```bash
apm install language-context
```

This will install the original, outdated version. The version of this repository is still unpublished. You can clone this repository to Atom’s package directory:

```
git clone https://github.com/massifrg/language-context.git ~/.atom/packages/
```

## Optional dependencies
It is recommended to install *TeX* language, via package `language-tex` or better `language-latex`, with the procedure explained before for better coloring on *TeX* primitives, and `language-lua` for embedded *Lua* code highlighting.

## Contributing
For modifications and discussion about the packet, please refer to this [repo](https://github.com/massifrg/language-context).

## License
This package is released under the GPL license, v3 or better, see the attached  [license file](https://github.com/massifrg/language-context/blob/master/LICENSE) for details.
