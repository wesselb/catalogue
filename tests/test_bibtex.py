from catalogue.bibtex import AuthorEncoder, StringEncoder


def test_authorencoder():
    assert AuthorEncoder().encode('First Last') == ['First Last']
    assert AuthorEncoder().encode('Last, First') == ['First Last']
    assert AuthorEncoder().encode('M. Last, First') == ['First M. Last']
    assert AuthorEncoder().encode('M Last, First') == ['First M. Last']
    assert AuthorEncoder().encode('M L., First') == ['First M. L.']
    assert AuthorEncoder().encode('M-L., First') == ['First M.-L.']
    assert AuthorEncoder().encode('M.-L, First') == ['First M.-L.']
    assert AuthorEncoder().encode('M.-L., First') == ['First M.-L.']
    assert AuthorEncoder().encode('M-Last., First') == ['First M.-Last']
    assert AuthorEncoder().encode('Middle.-Last., First') == [
        'First Middle-Last']
    assert AuthorEncoder().encode('Middle.-L, First') == ['First Middle-L.']


def test_stringencoder():
    # Test encoding of TeX modifiers.
    for k, v in StringEncoder.tex_mod_map.items():
        res = 'pre' + (u'e' + v) + 'post'
        # Check a number of common formats.
        assert StringEncoder().encode('pre\\{}epost'.format(k)) == res
        assert StringEncoder().encode('pre\\{} epost'.format(k)) == res
        assert StringEncoder().encode('pre\\{}  epost'.format(k)) == res
        assert StringEncoder().encode('pre{{\\{}e}}post'.format(k)) == res
        assert StringEncoder().encode('pre{{\\{} e}}post'.format(k)) == res
        assert StringEncoder().encode('pre{{\\{}  e}}post'.format(k)) == res
        assert StringEncoder().encode('pre\\{}{{e}}post'.format(k)) == res
        assert StringEncoder().encode('pre\\{} {{e}}post'.format(k)) == res
        assert StringEncoder().encode('pre\\{}  {{e}}post'
                                      ''.format(k)) == res
        assert StringEncoder().encode('pre{{\\{}{{e}}}}post'.format(k)) == res
        assert StringEncoder().encode('pre{{\\{} {{e}}}}post'.format(k)) == res
        assert StringEncoder().encode('pre{{\\{}  {{e}}}}post'
                                      ''.format(k)) == res
        assert StringEncoder().decode(res, None) == \
               'pre{{\\{} e}}post'.format(k)
