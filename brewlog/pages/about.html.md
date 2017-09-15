title: O aplikacji
updated: 2017-06-26

## O aplikacji

Aplikacja brewlog powstała z potrzeby posiadania prostego narzędzia do zapisywania receptur uwarzonych warek i z takim zamysłem został zaprojektowany jej zakres funkcjonalny. Nie jest to ani zbiór kalkulatorów piwowarskich, ani tym bardziej narzędzie do projektowania receptur, do tego są lepsze programy. Jej funkcja jest głównie dokumentacyjna, a dostarczane do niej dodatkowe narzędzia mają na celu ułatwienie wykonywania podstawowych czynności, takich jak wygenerowanie wydruku etykiet czy wyeksportowanie receptury w innym formacie tekstowym.

Aplikacja została zoptymalizowana pod kątem użytkowania jej na urządzeniach z małymi ekranami (telefony komórkowe, smartfony, tablety), co nie oznacza, że na większych urządzeniach nie można jej używać, powinna być tak samo użyteczna na każdym urządzeniu. Innym priorytetem było jej odchudzenie, by zmniejszyć ilość przesyłanych danych, w tym celu ilość elementów graficznych została zredukowana do minimum.

### Udział w rozwoju aplikacji

Aplikacja jest rozwijana w modelu OpenSource, dostępna jest na licencji BSD (3-clause new/revised BSD). Kod źródłowy można pobrać z [repozytorium Git](https://github.com/zgoda/brewlog).

#### Na zachętę

Aplikacja została napisana przy użyciu następujących narzędzi i bibliotek:

* Python
* [Flask](http://flask.pocoo.org/) i biblioteki rozszerzeń (Flask-Babel, Flask-FlatPages, Flask-Login, Flask-OAuth, Flask-Script, Flask-Testing, Flask-WTF)
* [WTForms](http://wtforms.simplecodes.com/)
* [SQLAlchemy](http://www.sqlalchemy.org/)
* [Babel](http://babel.pocoo.org/)
* [Jinja2](http://jinja.pocoo.org/)
* [requests](http://python-requests.org/)
* [fixture](http://farmdev.com/projects/fixture/)

### Uruchamianie własnej instancji

Aplikacja jest uruchamialna w nieskomplikowany sposób w środowisku dowolnego kontenera `WSGI`, przy użyciu standardowej instalacji Pythona 2.x - nie będzie ona działała na Google AppEngine (co nie znaczy, że nie możnaby nad tym popracować). Do działania wymaga bazy danych - w najprostszym przypadku wystarczy dostarczane z Pythonem `sqlite3`, natomiast pozostałe zależności są instalowane podczas instalacji aplikacji lub przez ręczne zainstalowanie ze standardowego pliku z zależnościami dla `pip`. Konfiguracji należy dokonać przed uruchomieniem przez utworzenie pliku `config_local.py` i wpisanie w nim dyrektyw takich jak `URI` do bazy danych w formacie wymaganym przez bibliotekę [SQLAlchemy](http://www.sqlalchemy.org). Innym zalecanym do utworzenia plikiem jest `secrets.py`, należy go utworzyć z szablonu, który znajduje się w pliku `secrets.py.template`. Zawiera on klucze autoryzacyjne aplikacji dla zdalnego logowania. Aplikacja w wersji oryginalnej wymaga jedynie kluczy do identyfikacji przez OAuth w Google i Facebooku.
