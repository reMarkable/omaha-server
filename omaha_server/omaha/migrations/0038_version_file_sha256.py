# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2020-05-11 11:14
from __future__ import unicode_literals

from django.db import migrations, models

import hashlib
import base64
import json

def add_sha256_to_existing(apps, _):
    Version = apps.get_model('omaha', 'Version')
    # Work around a bug in VersionField:
    Version._meta.get_field_by_name('version')[0].number_bits = (8, 8, 16, 16)
    for version in Version.objects.all():
        try:
            sha256 = get_sha256(version)
        except IOError:
            print('Could not read file of version %d.' % version.pk)
            continue
        _update_without_changing_modified_time(Version, version, 'file_sha256', sha256)
    Action = apps.get_model('omaha', 'Action')
    for action in Action.objects.filter(event=2):
        other = action.other
        if isinstance(other, basestring):
            try:
                other = json.loads(other)
            except ValueError:
                print('Could not get `other` of Action %d' % action.id)
                continue
        try:
            action_sha256 = other['sha256']
        except KeyError:
            print('Action %d\'s `other` does not have `sha256` set' % action.id)
            continue
        if action_sha256 == action.version.file_sha256:
            other.pop('sha256')
            _update_without_changing_modified_time(Action, action, 'other', other)
        else:
            print('Action %d has wrong sha256 in `other`' % action.id)

def get_sha256(version):
    if version.file_hash not in _SHA256_CACHE:
        m = hashlib.sha256()
        for chunk in version.file.chunks():
            m.update(chunk)
        version.file.seek(0)
        _SHA256_CACHE[version.file_hash] = base64.b64encode(m.digest()).decode()
    return _SHA256_CACHE[version.file_hash]

_SHA256_CACHE = {u'59lUTF2ov7g+Sxtx7tDDhGFxF88=': u'cmast0zLakvKKiVVbCmIQVNnmC1/8sMApdGyTxWTvGg=', u'KIvTuB3XyIfrvWcrnBL8MO77WBg=': u'Fz2nkR+IjeZISdn0VVBSUbj3QRvO81K+Zm+uBvbP3Uw=', u'WNQ7X7+z0pFHgD4h+PxiT79FAuk=': u'wmI2f1zr7AQ+LT+p//CSQ/M2IxXWh5gLq2k1Qmef7X4=', u'AR/pctZAWRDbpl8hGX7FZxfwoLY=': u'6Bg7ZoYt3u/zfwnv92R2JzGIRxOWGvETHTTyvKL8ZuQ=', u'QN6BGTmekpYxmLpyCBUFFoqYTrM=': u'H5K2ubfZUtbIHguwpSX20ShsJFXO7poIdnVuSVCblZQ=', u'kHFLUh/JdiYNp7UrPeP6Dklwh4w=': u'32TUiv1h9YFqbw+GLXH/3LurY4KB3L301H1sMXhnAVc=', u'rX7KVzR6Xfd6xteeM8e4fja5uiA=': u'St2ZCeMQf/ciOT+Z8pyCIdGAFsO9PCRgRFKXTnAmWGg=', u'6ARD58UEddcCd+pZgToHS3ejS2M=': u'en7Y4/siLt0/f7VdQozeZo+8IAsjTPee9oebUtwZxVA=', u'lsYi+mf5kXnrw9ARwl6pRQT//Bw=': u'rw5QjdvqBPVMhXw256g62rnqFGZ3zryuxiIUtm/n1x0=', u'70cGfWqKytV3yMLmx3IOKAS9LZQ=': u'w3UBN9H0newbVPvmYy6u0rx2p3f/HYauB8ybYujEHk4=', u'WArlaefYdI4eiRXOuUXyGJ5FZj0=': u'ffuU5yZ9/smWBfH2EAU+JjVgbVnSTGyscnkwo3dUNPI=', u'YVLjZUYl85+LydVioYnX/N3hy/o=': u'nfhOFGnbyeACbK7Y1aeKzS5sRl19uQWvYt5iuJlQCwY=', u'01O8+VPq2mDSSlEagtmTSB/5f7g=': u'hX5QFnMMPbNs1GCqN+9m3pMeufTI6evVH7EMmGRDSjA=', u'DwsQmlXkAQWcy3a2MV9v/ii+RVg=': u'cT+txodXKvvb0uyBz8UZ1SnpYyrDemCP+6T/1tEq2rc=', u'XudIqS5IJkdTbXCJDRNmdN/HJQs=': u'/KvJvhl0KwTROBKCyejjoZq3nTVm1F6tV8s2DjIzOzk=', u'cdqvpiISswvVq7IZgWr3U4hLWXw=': u'b2ivOq+n5Xdm3G1UX4+kJGm9S5PJsG9oFEYxUkua4+s=', u'PYWaMyLUwnSG/HSQ/Yk/J1BO8tM=': u'9DjON+KqzEZ6UeI2vPVRvgamYPHYWb12u8JG5WZC20E=', u'7D7Uc4HpE6IWYZd46jAZDR4bXHg=': u'BT2zGuRCyToPC8z/jdh1/CD63iMtLTzeLCu9f/2eUm0=', u'pQrY1ZZFKOCXZZ1q7vos/3xx8cg=': u'Qg3qqbKWVjshOn11ExQQRdYNhDWLu1d5eCheVPku7Jg=', u'2sJ7g72jN0wKUKzD8awBu+/EnIA=': u'FLgyV4wMFFUco4l2w4m2bVATaLfn/bvwJRrtwHurGW8=', u'RKdVhJLYJSw4615il8wFamByPD4=': u'xgoayIj0GdhjTUBtl4hIe12DEq+ZWCVlcZjmFV0R4Wc=', u'BE71i0r6hcT01YZzhOMRZumsSDU=': u'zpmnHtxZ1dEg7FrjENFURZQh3YUk3gboqk5nQYxTRXg=', u'sXEB95NtbDgVnzUQMLIUh7uEiFU=': u'ELTc6HYGMKI9JQFONuQgq/FSqoYNvVRCrakToasjf+8=', u'OEO79r5zMER1HhtJ8Om25F0NPk0=': u'6KWgTDL23P2s81rg6ure/f2udnY0DHBzwUPlRQP8Jpc=', u'pmt/RDYVdSeVNr0q0Ml2/r/1Bhs=': u'brHqrusIQRDJDwnVPquzp2qt0NERWmg95B6l102HxMk=', u'0Df21+YlMSDP/LGFaD0I/hZBvGg=': u'kNZKVtsQwydHCSq/TYBM6dkJdY2eJTX4XJQfAd9p3B8=', u's+TTE5dlumq6RD52D02Fd4BstOA=': u'YcwkLkoP3V39rsre3Rc49XHfX4lzOO3hCdIu7XXE6VE=', u'tT2eHIFNb9XOxZLppHHq7TSr2AQ=': u'J4KkR1JdhXGLEgzxX55XUgDogxDiV9NyPAolzeoscNc=', u'yg39GPZGWeWkW7HWYYNXkX14x0I=': u'Lm/1J/O8V9znMZuziEikLG21onGL8MvdV7YvlWTQW/E=', u'kz3VqaGGt3vI0ucyDoNfr7A3VrE=': u'Z4ThwQmM4h+PPyM3F4XSK0w5QCSeqpreOeDCfJFFvmI=', u'tx09qyII87Y4qsnCcDlRMWvIRnA=': u'9uCq8CiqmWlurAUBFoqg+0qUCBq19Veu5VsHgHB5Xvk=', u'5sDCk0pCFAzLI4dtktQiLVZuasE=': u'V3PD9ky+BAzyn1UY/1QRnWvR7iWaScnjQq7hFtgF7EE=', u'RX3vCzWFLWiuTTEVyCqWrMbQWfU=': u'E2mfjICqyPsHv7CrwsrkS4LTgtUA9YVBeg2J6QHOXjQ=', u'+S7iUVqov/C85r1k07xSJb2MNO8=': u'+ytQpLrKz0/tUy55FVaklcGp3PyW9kl3Hjkhno7liiQ=', u'aY8TUXwCTdknsW57aeyfD/z56Hc=': u'ORfER0hxlxRxP7rlRsvkTjyiTwJb52iqORXRH35Hz9Y=', u'miKjHVzQ1ac1iR2AlrBv/nvknPg=': u'IejUM/iaFdkN4noRVOhAdfvNpleFtjwBrl8E6CbRg78=', u'fAvQn8VEORGJ5dKpOKSYlrdnZQ8=': u'p7vdwvWUWQXnEB/VpjGyc0tElz1o32IdfTSZ6IcUMAk=', u'vAh2LeQNXDg/M2IhjaTcQNdG7rc=': u'IITV6iFEYsei+zQ9t+9wGNOyShd2vJW1Xm5e3mRB4MQ=', u'TWwHVQN/3BHwdEHno4r7HGKdKFg=': u'1pW8FJXAo51Qw/hg2fvVT5u2OFE+9oPhrdn+/jbFaxo=', u'dQp4dyJVmdphzqLiYlIHefq9FwM=': u'yg5DSk2YY2drfFUwHft+NiL/sReolQNOe+kHwXFbTEg=', u'u9Ww+d8m940MmW0bjpWd/017+Vk=': u'sjWgq1aBIx9t16n0x0TghMpR9mcWxoDbJ5lw05wvg3s=', u'Co2ozbg5rrEmCwWsyQVHWpFTouc=': u'69uVw1jgYH7uSoi7J8i9HPWkycXQ/DUl+pduZYqLm5M=', u'uJ0axtNfWRY0TVwtqxXTRCCjYP4=': u'sFkcCV8DpvFOZj3rPVgRR41yS3cNvHzCnhkdSm5zi6M=', u'/QbjdOj2WjK+SWium+L3qcRKfWQ=': u'PyW/Xs/vjBIXm58NMoUSrokuHI0SfqJf3RRKwzXlQfI=', u'4aXmnKA1hK7qnB0ZGqwdFYl3CAY=': u's16NgBhBVM8GHegMWwwz/jfai3lb5nkIJpjDECVWCcM=', u'irK7yYeAE9x56EiGN6pc2gaAAhw=': u'jtJfPbUvqQ7WDrR8ncAWnGFznn8Soqz05b8J4tsNw/M=', u'3Igvm/zmnFgJTfIREQjuD4I9DfE=': u'gh1uK6Odpe7Y5HRm5njxli7Ifi4LEfdXngbdUgjEaxk=', u'n7iGCwXjK2LhvQmXOXYsNI7UGds=': u'LWhm9ydoIITSKU79TrVuqBxoSVTzWvaKBG2VgO/m6yE=', u'8qG84p5LizgSXoK73v5E7hudjKg=': u'aYKxn6OJ2ScAKX61XLiRlXRQZLQlKSAjKZjg8Lu45Wg=', u'/SrZaRGEz9w0mpT/n8wDswkBo30=': u'p8J9QRGYxRELDVFlEMU/p53g21Y+ninNdLf+Gej9cjE=', u'QOoR+OlAxqErzITwXGO6thE7JIE=': u'RxIt20fSH+BgT1M+U5PQ4222RYG7lFNj7Li/ex9rQPI=', u'1vUatC9XITl/MT5+pJR4Op5NQ/0=': u'nXyyURUvEErYKkzQgqp6hvzqpmffjrWdCZldJy6tisA=', u'MoTzHgJWo7M3rEDQv4Riz4UoPJM=': u'PftkGP5XLTltdp+SiRnbO+yz8LS0CBfF8Dkbcsi0394=', u'IBAfqUaqSDsYoKAKOugOnhLJJIw=': u'tdZqs1i43tG85Z31LL+yuzeR2cltmcEPCu48m+dhmHM=', u'QzE+lsSK3lbYTNnE4eWgpqKwi78=': u'KOVj5l9YGeGNsHd1zJ2Y2rkEv4VK3qNGJw8qLzzRFjo=', u'vFjdGD+/2UuSuek/AdxXwrkcmt4=': u'QM5YDU3XZL+pI/316vOk5uIKZ/DMAZIoC6U0AeRzkJI=', u'rH0u35tmLCPkDdn/zO6Exk8B4Tw=': u'MNNp7W8cCO8/kynvk1AyEv14RpuIkl8rZtWR7jcJPVo=', u'J6wX/33i4pgn+xqGdi6ERVdkylo=': u'QtYHankJhfDktLzqbyHTxiACo21tNNFxWt72OXTbjs8=', u'eER4sr5YZgVYNw4D03kxVTRzMMk=': u'iFmuVirVj9CZINPqGEFU6N/sERCJE5bwqrHQ0uXWKrc=', u'3U/ptsO3lLSm4jTwkBu78chV3cI=': u'3K84HFU6FYt4vWKxAUCUvL9KY3eV5jF8JrcuWnC522Q=', u'2GGG6orMIMkCaZJud0c5XwWwc6E=': u'R5CuE8bNoLBHs7rxz+/z2d4IEaXo4T/MxAhMYDxOkbk=', u'dR2M4u/4d0xkIuhkkE7GTQDWKAY=': u'BAum4Kflz29kWXumSXMa/BaVcY/wPN8FYrYxn4aToOA=', u'Kr+HBCgccbKPlAcBsWG/P4pUZU0=': u'qIbLnkq8+mpctZpozO3xQj+agQ52dqcKcW1KSbmuqqI=', u'PlET7fXQVrHVO3eP/ZExiLtsNRk=': u'1kz2VigYNlmc6QtqXFNhIOLb7N7LQDKJoBeF/HK9Zr4=', u'CTUuP3K5ZBMmU2U7HxfFdDOMBTE=': u'c0Lpm7w3qVD4Wt5wCSXUHM0mHc5KbVbZR3fKilOF+jI=', u'eSOR5CwALSuqlwmrUlXHngzS3ng=': u'A/F6jRKHzKiOrHulBAj/alRCaC5suM6IcjIG95rzLAM=', u'q+lT1S4KTv198dr8mKLIaD6YNdg=': u'UjwXRosq0c2cmYkCTe+fBheya/y9lZe+B9pwzxgI9ys=', u'j3uIJcnKwrN/GHfquGZN/1dwDdE=': u'RPi4Q5VxIUDEyUTnnJOBeTKrluKu3DA2daxJRPJTR/Y=', u'97keTknSoNbUBY2jMdGglRWGUTE=': u'DF8TSdJX8r6IypvR5MJZfSVuQ76WrkA1WDfB96X3e4E=', u'PFnU0uiXd+09hxXWGSwxknsXqLM=': u'EBql3Rcq1ktciqf+ne4XS3d4ERURHLeD9aDdCceMrkw=', u'RTPyIF2AmyIVArF2+m85fItG4Eg=': u'gFhZmjWRPg1/QX8YBWbub0sH/PBlJlYg411P+62YFg8=', u'dlZlJB4wJY3KoUhDZolnLgjqTmE=': u'T4uFW+JPeReD8duAzk2ScpzSrjlpjCzqI0NHIYv3Igs=', u'HQSfMYBdAJLurMer0CDrGz765To=': u'd09WO+gTiyriVj1f9KftgAsaWFaSpwOP5RX0mmNOxEo=', u'A58hxmuUSt/nPH0eO7yvnWn6Oyk=': u'iCT51B1p3qlcILFIDS1+daS+Xy7mR2KgGl/QUF2wGcE=', u'SGUGjci1k7DJ8UvzoHwsPdrG08Y=': u'LzNMP3bGefMgiVsS9+hyUZWzJb0mxogj9v85Vye+puk=', u'SMRNGcGseW4vurrhRK/ilD7pNsY=': u'BylU+BvdQJe5cCGDAnbp4I1yATcY6uF/y0qkvbueFKE=', u'tSyQy9AOWirfToPEuzVXLpoXPJY=': u'fBVII3aBiTdT6m/LiXtZeJbbKsXuO2DSI4rckO4i+m0=', u'IsY0F2lDthve/CjJfioe4/2OFCQ=': u'8huGgMhJr4Z5FFolJwb6cPnyF7JQVV5ob1m4RXmmA74=', u'f80NSIOHTd5XCm5+rXJ0YRLO368=': u'NRI0yoOz2XX7k4el34CduoxjcF4f+YiZ3RQH+ufclOI=', u'zP+zJ4Rgts4AMEjkp1Tbz24BE48=': u'UjaXK9bb1cy1sSANuALBSUVVRSH2+lFMoLNMD0WVuzU=', u'FfhI9+0gghTjv2b6BHfFdPSd4UY=': u'Yc6iHdHL4gD3ASIvE98t5jl02qc8LA8BYHina6JsY/Y=', u'wYYn959x/tUGLF1gjQ6RyGFCPms=': u'ERSohan0ttbMpl6OlRiQdLRn0O6Y+OZq6Caa/Wr7qZM=', u'+3CVOPbfh0u1RtaGSwWOXSPvrC8=': u'B36fNXQxoNugr6pUyIogIHi69g/llgcCWsHm90oXh1I=', u'kbMiuM/HyUV28nsI9iJZZ6sCBjo=': u'yFmMD+CYzzXauikqQoEE2qDMTFrV3CxBvrai3N2SZVs=', u'kNqGZ5+cigLt5ItUW756xgECflk=': u'ao1hZpPlEI/pihOk5+qZQtJr3ttzK5mFCcEdYfhyDTA=', u'Gn5RChfZDvyKqL3zwqgXXJcCDjo=': u'JT+At/+JejzUut9XQn689uXv3PReRWwovDLr4ljNBEk=', u'FV+fWctOLzgVEd+yvjMF7llZ4w4=': u'R883p4vw3BtgUlfEDswU/1O3HWmmeiO0eENotmg5X0s=', u'u9XiBvtivl213MV8HFGrZ6Hcg9M=': u'/Mbymax61LuCs0kSHsXTcU25g8d9Sm9lgSgfjxtC3Rg=', u'VZNEVIx3Uj4TsquEGpIZyrN8X2E=': u'geQKqIoEWsj7y+7yz5AOw1kWBqP5GNdO82gWYi9m+ec=', u'dQrC+FoGLTHOtkewTq2kMy9/X3M=': u'hRROuPlr/8dUz9jKzkbGs3amb44zIN1kHYVRUA9NAmI=', u'Rk/OyLkMq13XQsV/qYWfgMsJoes=': u'uhl90qsWFTxS3I0aWj59Kle9RjUp0TYYvNre+8ZBRHo=', u'jL9HVqulFAJIES8GpcbyBsSj0s8=': u'8f45GJcQQk2u6YRADh52221eeu1Xm3LZ6VHFJi+yXjs=', u'pe1tganfkgcXBRU/iPUf+hCbP8s=': u'RwRoQ34jBkWn0iAl4CYnPglGGs3Konh2Yt/w6QY6czk=', u'UEssu0A98PA/ZAmQY6XNV7oB7H0=': u'1sRhu2h+dbAV10vEXEiWyQE3ksfR2ggDgHy1O+gxfcI=', u'xY44fmXZ++v/UyVdpNOGfEzY6RM=': u'bupj3GEmo1MdcZmit1iiJ9VPrPXUkcFIfenPaSCbQlo=', u'uLt/FFJlw7+Rp8cVw8UJf1kKVe8=': u'ujJvpG5jPW6QhtwmBS9ZqILMGoMRtqZqYEPoXOwgss0=', u'Sm2VK8Ovlmbfb1bB005DSCFkRhs=': u'MloOO9zcIsjr+vHe0DzVu7MJj8MSzsKq1dmEUaVXhNI=', u'jLtaG8lau62+PkzpxQbvCDrng2M=': u'ywVSPqrLVb+PxI4KpfSAvKNPAuDQkh1miyqCAgmc89U=', u'PUa5/IO9+PUu6FldM3fj7ZD42Oc=': u'/n1NAMyEgh2YTzhGWEoU8dMgGiLyfnlwGJjus+WktcQ=', u'c55ThJZwMgvZtj+OHaJcrsJeFJM=': u'b0UH//T/J7YyFHW2kMyGw4C3X10nd0Nt/vx4xEMhipA=', u'77/4pBZKAlc2ccD+3cGc4C5qdRU=': u'3MwbaKdg+V5cnWeFLew+303ZFh9r/uZfFZ7HXcNdPzU=', u'AAwRuF86P3NS3bf7MEaInr0DdSg=': u'5JhryfLFyZj6/0lIipEy8KVpFQPjfSWSdSpz1Jfmbpk=', u'ZRjBz0KjJzgumgpkTXkNVYJsHJQ=': u'TD5dnL7RP8bB2caxBwB7MILbEKgOTfup23wqou4jPNw=', u'otX/RD+d4VnrIKOex6oy2d0A1Lk=': u'74XD/IZPhXfwhQPsKD3B/xm4+0I9hv3ksN5BsILjkcI=', u'85/5xjHJqcLnpBlDh1gVrlwNb80=': u'5H1EJ82MpHXugc6LEeO5wPWhlCOM8ZpMAOAX+NHm0ec=', u'KEq6IqPQB2HLWYNhFS5Utt5qM+Y=': u'1isI1BHMeQs5swLnzrfEvNJqBWXl6lHcGwlGcWL0zDA=', u'6B/fQp5kFCYIPu9al2NK+fHhu1U=': u'k3VWNlwmtrMcfJWmBcH+qibzVLfCRxWJjhIanjzLdFc=', u'kgZCgjWmmy0B86GxO3h0+FoLax0=': u'Wy4cgCUjAwNhJWAEcYzLZNx1TmdYQ2tBoIppQlnypmc=', u'OgCbXh+a9wMaQbXKK1Z7O5u4JDU=': u'HKCKS4PFRyY5rGkZzLmDqYEFFBuhSoXalYxCIqdFIag=', u'q7XV9WHoNVa6TU8m2MwDzHEiLrk=': u'xkbax7XLoc1NHURdwBBzma3tO4K3E8zE1W9ikXzSirc=', u'Bmk0CzZkFIsivqCwa/vxx3wzRx8=': u'R9xi551st1iQrceeEcwvuvxGhMmrg2GOzYPDG3q/6kU=', u'Eoy7LwVpd5fzOh8XBr/7WOWO5pc=': u'PQNmeDOFmpkkiQEGVvh8Z3HKPfJwSHhrycIlXeZ1SVk=', u'aGhbaFl8gNmmnuastMIngIZq7ZE=': u'6kMZDngY0p6ginNfCxsTfbhWhog+ibXxyzjttM0goqo=', u'fWVZofx9mxB3VZBg/D+fX/ZWC3I=': u'qV3CbElvGjVNtBGorWVEI1IafwUXDAuu1DS4WAYnWLc=', u'IcOtd0MG5NREWq7+/kpljmXkEms=': u'QDhC7DAmD2l9g7jVRGBOhCFMypW1+Md0Nm7aiRY9mZk=', u'YGDnVR+u0W0epK5/Rn5GFSQ4/uI=': u'ud6OQi4HSDRY/r4a8AsHyqmBkuljhDHevZec1nsn4QE=', u'BkIMsG/BpQAs9OA86YX9jfsXvc8=': u'pgFwP3FjbceJpEuuHn3aIAMlUmMaMP1SFaWl7mg0qGs=', u'+fnqV8cHAGVtg12Ere/fmv6Pxd4=': u'TJ1xPfwO2pob5rsOwvk+1T2mevnL8oVnEy/EpwJLY+4=', u'j6d99K/f6XPB7+xZ4lWw6Cx+myc=': u'TrgmcDarxIlCIXT9HfnxiPBtZAYj7qVmEf8NvJwO2tk=', u'wueZfVGP5bnx7wytgn/7RbJnW2A=': u'sp42aLZSAhbLv2p120PSxHW6ZeLaZmhUIcMZNBF5XV0=', u'5tBEjunu+l7j6KRyl1sC1RcZ2d4=': u'zfA5PHtYpxRno8gvQ5QZrtgVeJh3Qmwvm8mpiEFbxQw=', u'GaT7lCHMRjwoRzR33kZyA4m3jP4=': u't6ikOuGohridKBL63PmHDqj0xMcaCxNgSsaHwHxuQRE=', u'bOMbeKU8fWfhUMU6OTUZZktZSaU=': u'3uVPugu3ldGN8xTgP73uxp0+uhRm7ZarsvrmGj5g/40=', u'ooHb/YCHrq1iFDxJ6/eW8xg6y3U=': u'AkDWw1Oj62g3YpzOJ7/lhgPfViFxHRNdUCtyg2jy1F0=', u'EriGC/LRrXQReIRRpAtzwh7553U=': u'4wnDlUO7nIpOMq/IUgDp1hUaHx6PVU++idS5w5mX0hI=', u'fOW+nrfV47tqZT6QL96AQ1c6A5o=': u'OniTd+JjtJAuJJfiXfemYmehc3WBNxMOqFCixAT7IZ4=', u'Hh+YUKVoYT1s2futGv64gs4scGE=': u'VSJSedeIRxmfaOUjXscDvP8+nnaFv8gkyawBJ2EAawk=', u'NShfV0/NF7eroyCl3YLw2lq9cCU=': u'FpyJmH41JaJKlYe4rsfmV/47fam3luz3xrlmqIplurE=', u'W+cZc9isC04MHajcEAIPDTaV5LI=': u'K81slt1X7E2r2jZjO9nJKeCfwoRHzS8fef7QMfPsnmU=', u'AGfRxxEIn2kyZ7hDSRkw9ExqMUw=': u'0K6pEsg+d7nIWC63bjV7gsx/dLVngbwCNWnJ048YVBY=', u'b/8D4J5o8D6Q603RXn1LOwAKxtI=': u'f7hKOcB6grRjQM7RnqGyqqAijQQK+Y1ZMwzpQBJzs8Y=', u'457exQSHxt5vFW1iBm9NrcQhct0=': u'CUn0rVrkVv8YpOIyCG96UD6+oU5EwFDnlo3BKNSfrNM=', u'JlClzjSFDO7m55ZVv+yqBJOu9cY=': u'wrVfq6IpesEAWQPGb2pjvlp1qw9sRSkC2c0AzRC/VO8=', u'D2LeOz+FY/uHJ2h/zIwMyTtJHRg=': u'cexe009wTiG8K5zwqteQ8W0TGoSpfkKI2obfhTc415A=', u'uCwlb6wndDHVHZM2wYTv92Ju3zg=': u'7C8PISVT+PDi5MhAD6svk5gsOXXZ5VsIa3RDxxyCijI=', u'x7fV7ZvrSVz/ZgMO0IEM6LgSwd4=': u'cb4iWcefsJ2lWZ+vbfF0G75ULMSj88Lb07G69DEV5Ik=', u'3zW5Mg/imdJhFawL0N9XMdWbq7I=': u'pPI59RHicuVZZ/U/DjeJDlEP+D3e+7kVT4/hHtQqdYk=', u'UA3sGkb/c0XnLw2c1UWjHdDcQSg=': u'8AiKA4Av3BQhv1SecytNoGspvcztklvofKwdkjExUSs=', u'aENtGMsujBzaMKdLq0IfMTAbMO0=': u'iwGCQrNj/Y8Nrh/DJpIc8D1ZwxQiVsJ4bgUeYEnfVHg=', u'TTmnp6+tnh4CNlN+2i/2neCcx6k=': u'Ma7HICAupduu3sZ24MTCsB81ZnSxA5rLBArTjmqh9Ao=', u'fWc6MW7OG9+/n1kua13RspM7IYQ=': u'+T9vAupd+cR9jouwGeju7rfYJWWlOnLd30MxNsu/rZo=', u'e8G3SZLO6Rr8s9Ko1NS5KiyccbY=': u'AJxdAdI0/c6dtraLytGHkm8Hla6lQm9jm9eFse79j+g=', u'TONvVha5QCaZb46nG8dXpvL9yVg=': u'huOWubpzAwQLOxRrsJ/+GvFMWCL7bbzSzL90uaRueRI=', u'4AcEr5sLyAwMsjxLW4jBBM3e19o=': u'6D8t9nkWtMeBqz9c3pEYZuqC8xMuONQAzfCpBxt//Ow=', u'wBPxD/c7FnD86YdqjUbstZRQ2IU=': u'OooZwhxOWdA9qgXCdMNgHQGVg5cfqfSHucFBa7SbYN0=', u'lBKBWBl6/iJTbClnoXFfE3jdVsw=': u'/qvN5A0cGtz+LYB9M9I7Ky6mtmo14f74QCHuG0aQUcY=', u'6g8zPSIwGFuLSaHFgPVarJCMOSM=': u'iUgphnQZp60UO5xYn+Ebm9Tc2n0bP4RPgYGnbQKXiqo=', u'1kno368DxYEoPEMqS8By3P40KlI=': u'4nbcfA3PCp87Unigty969li4181IxfLzf7XoP27su70=', u'STA7KtDOo20dbtqyZcV1lew1HYs=': u'5nDSo7UM0T0FJHdEnXDhen+beVQNQHrMt2cgMV2hGbM=', u'hKAUwd9zyKeeO23Za49azsLgGSk=': u'IVmorXA42WYHhsVOwO9oJJz2QP9eFTBt+p7+ooR33mc=', u'CwXcGeur5lYk0wVoXpfcvFJ+kwo=': u'ujiS8328B+nJ6CETJPM0Pp1mowTFdTCqY7WKkS3h8P0=', u'LEjo/pKo8ersDOpEDWFrHRR3oHs=': u'qTC8F70bznFSnu/c9dAcewtpdRn5q4hR1irThlhRZ5M=', u'aNwJ9TQUlAdK62feeLN9y6I4W9E=': u'J84Idjo2sS3lEt5ZdFQriaDOAhjbjd/w46AQT2OF1/A=', u'PD/GTy2g4LT5hzjZLrmTm1CjWQ0=': u'vpEjwM+8aHUrZnJiLCtkuv0oM92UYc2JPRP7SOygIqY=', u'eRpo+hwKNaFj03iaoRCSMCiVKpk=': u'88Yhx6To0JYyWNa0u3AkchtLl8z8Lo5fNdedN/0dIt8=', u'8y26OgcoyDIBKEyKA5izkY16u04=': u'yrgqgwQBfWp2BBeNrG2cAOmnyp+i/qYETeimK1ArMpo=', u'Zk2qZgWLizo7b95uKQcM9w0aBUo=': u'jVLGw3UFxDlvt0PN6nzo8n8zSYebjmqip1sIRvbRtLM=', u'Q0rfbKnOluYlnyjOIhFHNtUa8lc=': u'qT28wxLtgu31aPxTMLEHhdcPr3GMwh3nRBwXKe9JdLw=', u'TG/xGvIkIhebIaA/8URfRdzkFOY=': u'CkmFt2mpYaRZ8Im+iJIIKQAc/FEM0wO4e+bqciIm6Wc=', u'1bnl86INWTGD5T23Eo5g5Xa6cQ4=': u'BIWFSxbwZBl4v4d/7iH21jJp9165sPG8DgQ4yRwwoq8=', u'84Za/mXpIoh0NOld/aCGZvnZVFQ=': u'CyctXHj3PS1R1iewvjR8LkRisd5a9tkwfPud+XVOv0M=', u'tT9L/sDLD69Z531qoLCkciQZCBQ=': u'olwMMOZrF3QWrCW3fQwacadqURYPRhF60ZiSOZxsSgk=', u'3QNLx99LOi7qsY5WZCFP5eyXIx0=': u'JT6LAzKJckktTL0b7rPyUJTq+cLsQKKPYjtmKmm+TTQ=', u'ARq2l8KbgRYmJVbJ6Y409/YPdhc=': u'rR6ggYTNjBv/RzkwPAqRv/JDvAn5Ur2/tn/4qu9OO2k=', u'4VZfiOoQfer2BGaw/T97GmeUeJY=': u'5hToX2EaadFD+Em61gC5dW2yNcxfw0P8OxOlUEnmkTg=', u'sJHth+0Z+5ri2teu3G/2FOErjGw=': u'VAHH7wqXHJp13M2cHIVlM2Y2sBizMKTTu4WFl2e7Uc0=', u'LoGhlF8c6t0YCL5tb88/vQl+MII=': u'Et4Hij3/tTveUYTEvQB8r10kHBVcwdkJgCP+vQ6S2io=', u'njj22a3jtf79EtAI5M0D5yLcomc=': u'Nt+cr90A0XHK9/BKEjGhvhg3B8STtMoJijJNfrDCazw=', u'0DMtYvA8WQWw+93NcFaoZQ5128g=': u'TPjp11MDlBLVO7TOjAAtEsnScmeR5MqAoi29+8jUbK0=', u'pwXdDfIGrKsqwcw7mSNfyiNzSeE=': u'Ys1PR32sUmkQTZFWSUaKsgLfZRVjQ6uK3kdBlKlBJX0=', u'wM3eVsSstj8AkDAvIEsYRhHOqXc=': u'utCsZCh4rcT6GErR9F6ClZegk3qq3GqM4fUAWAq7v4A=', u'iTu4gswRBSOC6hHQk5I2UP4RyzQ=': u'WSq4jFGXC/VZam8IZs5ZX3Dm44E/DdPM+ApdCzEwS2A=', u'djH+LUxQIIjgvY/JA/2tLwsOX24=': u'1B6WGI9O577Yaudc2CEqS1UPZsbNGrp44TbG12dh0jM=', u'1nI+mkSLBaqasPkecz6zGz4DOe4=': u'zA0js3WLgCjvHkbYu27z1C8O1ZU3/HlCRhQ+/MPTOYc=', u'iIe5JOqjnWlG/XtMwYZWDvtq2ws=': u'WQTYfyNf5mIpUO5510VEbibbk41gLhjkLGtDs/LyMxA=', u'zDGxa4PxjxQiLsTMImGxJnj0itM=': u'gbgaFuAz0nUBEh/VyCNVMx0j8nFZ8ZSSLnxwuo0diSM=', u'Qu3mkfwI9S9BdXsYqUSTG1SKI78=': u'WEy2WzYPIRNHmStfWpkMvoAkus8kEx7mZrH+Jst9M+E=', u'S2Sjb1r7c4HuGJjuqr7APOVJ7iM=': u'rFtfuKGhya9iLs740japrnwjkuNwR1vCrGFrMlXpTSQ=', u'e/QFqtErF57VYlLoBqFnm9DIEcA=': u'HcmFdKDmXX6OIwi5BRtzalapj26CiT4nyUON7isk+98=', u'UtkfWthy36OL29HoL+8CrT8a8gg=': u'r1AxpywpoOqYXH0PFjwKDryhZ3W3IkI5iU54qiONc90=', u'roLq9NaZ4TXTsXI7E323GxmaEM4=': u'Smcni/Besorksea8pmcu2D7kWMUrphARLDQ0y2oGjG4=', u'v1dY4mKcBmXPWRBkhNpgNNSCsvA=': u'H7hK5+PYJ9lK4TGjhnIP+5XV5e+HsdpQwJ+CVGVAjy0=', u'YQm6k+/MHwhpi+5nPnDXoJ9263Q=': u'oX1e0gYg2aOJkOCpjUnDVg0KOVp1hRefUldwXJxB3z8=', u'XRItdXeo5ITpVPw06f+WqjyUsok=': u'2oKf6KxXJaGiTDUQlc+2Vjg6yN76NX+YRLDea4re7Ac=', u'KDDoTHWgSCx5//gEqwW4kOhFe4U=': u'eP0Q/9LXx77nIQsxBYXBrVrKmVUuZWkIa8BAQuytWYA=', u'FvIxT2xu96MPjaX5u7uEV3U6xT0=': u'XHYuyD1YsSZr0pOPeWY0S6dMWl9jGrL5hAZh2bo5Bpk=', u'rtoT/4oPSRVBE8ch3okpDp5dRiA=': u'Scll42XEBv1PoF7cjqeP9ymyYMhcH7XgNpHrY9YYv2c=', u'2/1JE6l+rcMx9TeQPi7YPYl0SII=': u'Afg+kTLvqAi/zWuQ4y7VAamENjJBkWnCq69qAnXijl4=', u'FmOhPxsvUwKp/Ez8EjjmWlYZXxw=': u'bMVIvojezGVFmvTNyQkIM99N2o9DUimjbAXZGXTUQkY=', u'jzYWqJPY2AbEZaIr+hJXu7jm5Z0=': u'52JeTC6ebs1p5Ebc0XHQhMmsSdQMVfWJEhIMzUrZGcs=', u'Ux77+YY5/s1XKxkM0OTfWDxNWgY=': u'7yHqyfkXNil+DuXRpijPyuT6ZiutIX2oyFgzgteDy8o=', u'da1dc2np/MSdtMpTKJtaSqzF8GA=': u'cDo6uaOyugi1nx3Mu5LQdwCqZ3//+hE2+mdfTUpQHxQ=', u'csDbtYiWkONbFNT/I+08rDHcgw8=': u'vbaXuNLLeyFXTNRT+ek8Lqn4h8fcJuO76hjctAASbJk=', u'krsV/UVUJV+pslhZgNo3y9HkssA=': u'UEv5nAGJJTPloIzEg+ZQDp51NUPG9MHVk1oba+7oL8Y=', u'+wnAPBoe/IOAcTXeDY2QoGKMG9g=': u'8jbwnYjM3vCf09Ui22M5U114tntsLRAguWNXZCXnWeU=', u'jBbj4pOhvSV2ajw/GIc23tB1kZM=': u'UJlrV/ulA54wwgAHD4vboWpTtPFGC70KhU7QQhCHcxo=', u'EmFQwCDSfRzGZY+kup7FDL9IVyM=': u'M0VFA6Hb+6PP6de+Hq3Fo4PCjkhdsi4ERXWZIdidtuo=', u'lX257iukweC2QD3kmEYdJ3+RgWk=': u'4MVa0VxcD8qs2NSemYgtl9BmDlagvcigrmwj/6n0+aA=', u'vffukR3G3JCoGd6/rao36O1rkdM=': u'yb7hMmblsNANwkRrL/DOcNI76rKUAIkV0Q+tfG1hQJE=', u'SYN7R4G8iXIWOie/pbr+wGDYI2U=': u'5mZ5r+ZX3nn6DajLwb5MmCUMCrP4kYsrJUVPGeiWMFM=', u'W3gjeT47vUMzYuwGVSPqeMizBqU=': u'sxJ2Gqrfu9wvX9WvNkjTEVNKgABFO7xCRJgVBwMu5nk=', u'So90d+78bGi5fbwm6eDqetsn2zk=': u'w4l/elo3v+89qdbeLrYpVnFBpJ3rzI05BCainAmIF04=', u'1hsuVmXNaUBwu5PCYrlQ8FPW6Z0=': u'PWXYCltXnrftKV/PCs7PyEo/IRoZ9z6kFTrhLxQBTt4=', u'A4w93+WnJKCpexftUmxCElZwrhM=': u'rJBWVUBwM2HoRkpy0nNIwEcFV30r5m/tVFcGZuZjZns=', u'Xo7BIFL3jVLbJJJHIeoR9p2uOFU=': u'EMI/UZdOxBaDel0m5tXnnPN7Z0cFb+N1Eyxik633f0E=', u'WmGR5+AGkpx1TjIHEGxrkTIZ9Dw=': u'HAvJ5P3qpCnVmrD0KIbkrALvH9b3pmr1OfQI0lF1UIY=', u'lBC0cMCRfa17t0tNLmnoNPqvQrs=': u'aXPLUsUB+R9AdylAvcoYggYpLr6UPnuwknVpwaOWZmM=', u'ey8pS/ikqoUvuvxDekXDK6G4uZE=': u'YLbfM74DxPWb2nzpceJd7iIH8SKNpAGt2IoiH89uqSk=', u'Z8yKav8MBqLd6ABAuLdRjuXWNOM=': u'IPJRMtK1GxgBv4dVEK485NlygyzKbA1eIVqZcf6ldJs=', u'XeI1/kKeKazBVo4DbQ+e8Byz7xk=': u'O1hRg/KUyx9NZ8MRmzLaObdogD99Q3/dMlcmZQoKTl4=', u'K5VkM6csjCNyYKMYCfZeDpCgFcI=': u'4fydiRd2JrOoxDdvhPbSo6/nW1YB26oXEd04ukyFWX0=', u'DpKRkI/DsDKkOrkF+nFoeW7yOVg=': u'++M+wGCRmC0mLiDUKos6hOXVk1UtxCheavkLXNQS5DU=', u'7btVkl4fIfL4bOZannQ1+BRqQFk=': u'M6gw4F2cPIyKpnwtHSyv8fn2w6K4uDCPIQl0WebewlE=', u'ks2ZvoKX559HHOBAJdtGvOgG8/M=': u'kfEnT/rewM5pTnrV7gDokUaoXOwoFGxcbZ/aaCvIGC4=', u'z5dSntUNZrZgxgi/B/U35MDWQGM=': u'Wshq85DByZbJQyos/7JyWoWYdtBt7qfN7aYkbAiHqjM=', u'mepvmyJtdirjd0MOZ5RateR0Rnw=': u'egdl/75xthlJJwu7DbJPA5kz+FNi7Ul+EvBvSff2mlk=', u'xuLirixXAI3AgXlOS/kWqJOq65c=': u'4Cu0jCwXLhhY8i6ArTcPKzLP8e77kBs0pRZe5gDynwQ=', u'Ph6JLhYtoXT0RyrgsEnJFPENwAY=': u'Y3n/RRGA0tfJIp4OQ/4A1auZUGcuuBPq8MbSqACECwY=', u'UBXXlJVA/idfHDusptraieoe9pc=': u'LoeUmjcqtkKreRV8ILZ3GIQvjxpC52B8s8d5xplA5VM=', u'uTDV8xZTL4soWCMPP25VdIlXK6E=': u'k0HMOrNwxmIx++cJFJ6FTJAO0MIB8i8Jtr3HOkhcQ/s=', u'7A9l5d34Gr3jPhJf4/BmvXXw7Ic=': u'MYec4gCE7vW/Diq6Ef2/GvCz4EMb+O18JTi+7dCUFSU=', u'wLNwLhYlwcPyeZ6S6Ps5GgZlFmo=': u'6kIXh5JDEL7fv/3mLp11aiiGMkzf485iWVR+8z25cms=', u'o5KiHTY0BtVzDJCU3aBG62glrYM=': u'p1xKlE7zPVdeQmwFWVg/bq9rQjr/mnchltu9F4qYvyM=', u'6x+QpaIF3/4LcwrTjKWdB67gOL0=': u'3NvfbjFRuLfxu04uckMxitjXPDvA5Ajlit890iGt5OQ=', u'xv7sSS0kGqgGwBcV8SEFfs1oWnU=': u'z0rf+3d6yHIQCxc5BYuxkyL8JEwkD8iAH4IoG/hFuXI=', u'Y8Q2+0nGIuTdoa/i2S0aeRisWO8=': u'ZU8jnc79ExHPzuumnwvYQ8HJpVeRvffSRvQBZ9YAJrY=', u'7hUmvyWvx0MH9V3n/5MOqsmyoMw=': u'dmIbTw+CTnSFEI2KdaBp9P8B4ZC5P1UQGmxvUXBUv8E=', u'UcHJWF94ClEjgcfLBr0CI8a7FhA=': u'1Yx9v0dYQjeeABZfKp6bXUtWKp3ORFdHgDyJk19g1Eg=', u'iqA7jUz+VQ5zOq5Jdgck/kUPQCo=': u'Ra/28GdCGCny0iEOlCl78CSid9SSSsHtXypuBolMukk=', u'7H4v31c1MuxLSdb9jPjZCtwHQg4=': u'uSs5gcmBITPSyM0UtEMasXz6ikUXN0ap43FAQLNlNng=', u'q0/70LSaLbNAqx7slDo12YBl/MY=': u'FjG6X4Q24Rq6VAOzbm8y3O02ZllnSYG0lURKvGweAHw=', u'ociIrVTVBnsj5GcWln2NlRu0G/0=': u'NResmZF9waN2hi6RTiZjOWXeXXp4SbESv+OXgSSuTog=', u'8WHr0paZ2TQRzsCRXFEzwPMimig=': u'0+tTmlVjUvP0eIHXH7Dld3svPppCUdKDwYxnzplndLc=', u'rfR4qeFah4UdrsByttKXp7tcJZ0=': u'A+Yo08CeloV7ntHlJ83YyOKEjmgr1mErld4axBq6iss=', u'CN82b93rx21qa5lwTE1IhQfRMTI=': u'GfVDWGgjKq3F/wdg6+tBU/8iH3Ii/ECrsKeni2n9atY=', u'IQEQfcai3Ahu7gurl3TDNr6guk8=': u'0/B6TS54T1Kd/+NEN2fXj4/SyVqox4fwxds0Oiht2Zo=', u'C03ByXj0yyjttOrF5aKnj1fA9cE=': u'8MN+6xOWva4F/gKpzmFtrmAzV1VWlLQYnc2dPwBzEa0=', u'VJPx9FxTFS2pZwSGwnWlIXKlIb4=': u'tmszjcldXUpxckFf6GuJSgQAm8jF8tv0jZ5eCREj1zk=', u'reQUuZk3JVU+nhZhXIWEIS9u2Ao=': u'lQWlfvT6DqMQxK3mm1C+1TcuUCaFhzYRJCHpahR6/Qs=', u'UzHdhjSVaCvaB4UQeJUNxX+zn7A=': u'vHJCY6fBd8kb58wvalCwiCTlwzHLvoe2JKhUZziCyHk=', u'sNdYgnDm4hYrzChVxFK4BMDQHRk=': u'YJZXTK4l4lPtecqZOPHLAV/5BsQdxj+c8oa4S7sQwJU=', u'BHjn8ojzdMI29lc3VM5LCcHtjyk=': u'0uPn0WFkGN64T1DX0P9MCmSUB0FTKP0BsMLb9v5mHG4=', u'SLA42I35R3aYWLmOD0HWAmNo3ZE=': u'/kRMvFr4UOhfAq1P3kmo1/Tj/XEHoPNOJnF48qIVWeI=', u'QHKxm9xDqRhxKS5/LoVECQOk8Mc=': u'FnF4Bl/VQXhRHO+55LPKq0fufdLhLfwXyqL5DCUrdtU=', u'svYwTwHxmPQENamOTsXSo08lsYo=': u'wc4Kjc11KOYnABdx5cUWOLtM4YvqC7SloSBAHI+OUas='}

def _update_without_changing_modified_time(cls, instance, field_name, value):
    cls.objects.filter(pk=instance.pk).update(**{field_name: value})

class Migration(migrations.Migration):

    dependencies = [
        ('omaha', '0037_longer_model_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='file_sha256',
            field=models.CharField(blank=True, max_length=44, null=True, verbose_name='SHA-256'),
        ),
        migrations.RunPython(add_sha256_to_existing)
    ]