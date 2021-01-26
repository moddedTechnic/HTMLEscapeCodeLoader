from re import sub
from typing import Iterable
from bs4 import BeautifulSoup, Tag
from urllib.request import urlopen
from urllib.error import HTTPError

def openurl(url):
    try:
        return urlopen(url).read()
    except HTTPError as e:
        print(e)
        quit()

def ascii_cl():
    source = openurl('https://ascii.cl/htmlcodes.htm')
    soup = BeautifulSoup(source, 'lxml')

    def get_rows(table: Tag) -> Iterable[Tag]:
        for row in table.find_all('tr'):
            if not row.find_all('script'):
                yield row

    def get_td(row: Tag) -> Iterable[Tag]:
        for td in row.find_all('td'):
            yield td

    def _get_symbols(row: Tag) -> Iterable[tuple[str]]:
        yield from zip(*( str(td).split('<br/>') for i, td in enumerate(get_td(row)) if i > 1 ))

    def get_symbols(row: Tag) -> Iterable[tuple[str]]:
        yield from ( symbol for symbol in _get_symbols(row) if 'not defined' not in symbol[3] )

    style = '''
    <style>
        * {
            font-family: monospace;
        }

        table {
            border-collapse: collapse;
            border: 1px solid black;
        }

        td {
            padding: 1em;
            border-bottom: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #eee;
        }

        tr:hover {
            background-color: #fafafa;
        }

        tr:nth-child(even):hover {
            background-color: #eaeaea;
        }
    </style>
    '''

    with open('out.html', 'w') as f:
        f.write(style + '\n')
        with open('html_escape_codes.csv', 'w') as g:
            f.write('<table>\n')
            for table in soup.find('table', attrs={'class': 'content'}).find_all('table'):
                for i, row in enumerate(get_rows(table)):
                    if i < 3: continue
                    for symbol in get_symbols(row):
                        f.write('<tr>\n')
                        columns = []
                        for data in symbol:
                            datum = data.strip()
                            for k, v in {
                                '<td>': '',
                                '<td align="center">': '',
                                '&amp;': '&',
                                '"': '\\"',
                                ' ': '_',
                                '-': '',
                                '__': '_'
                            }.items():
                                datum = datum.replace(k, v)
                            datum = datum.strip()
                            if datum != '</td>':
                                d = datum.replace('&', '&amp;').replace('\\"', '"')
                                f.write(f'<td>{d}</td>\n')
                                columns.append(f'"{datum}",')

                        if len(columns) > 3 and columns[3] == '"",':
                            columns[3] = columns[0]
                        if (line := ''.join(columns[1:])):
                            g.write(line + '\n')
                        f.write('</tr>\n')
            f.write('</table>\n')

if __name__ == '__main__':
    ascii_cl()
