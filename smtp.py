import getpass
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class Smtp:
    def __init__(self):
        self.__EXT = [
            'png',
            'gif',
            'bmp',
            'jpeg',
            'jpg'
        ]

        self.__params = None
        self.__smtp_server = None

    def __parse_args(self, args: list):
        if self.__params is None:
            self.__params = dict()

        self.__params.clear()

        if '-h' in args or '--help' in args:
            self.__params['help'] = True
            self.__params['text'] = '-h/--help - справка\n' \
                                    '--ssl - разрешить использование ssl, если сервер поддерживает ' \
                                    '(по умолчанию не использовать)\n' \
                                    '-s/--server - адрес (или доменное имя) SMTP-сервера в формате адрес[:порт] ' \
                                    '(порт по умолчанию 25)\n' \
                                    '-t/--to - почтовый адрес получателя письма\n' \
                                    '-f/--from - почтовый адрес отправителя (по умолчанию <>)\n' \
                                    '--subject - необязательный параметр, задающий тему письма, ' \
                                    'по умолчанию тема “Happy Pictures”\n' \
                                    '--auth - запрашивать ли авторизацию (по умолчанию нет), ' \
                                    'если запрашивать, то сделать это после запуска, без отображения пароля\n' \
                                    '-v/--verbose - отображение протокола работы (команды и ответы на них), ' \
                                    'за исключением текста письма\n' \
                                    '-d/--directory - каталог с изображениями (по умолчанию $pwd)\n'
            return

        self.__params['help'] = False

        if '-s' not in args and '--server' not in args:
            print('Не был введен адрес SMTP сервера и его порт')
            return dict()

        server_addr_flag = '-s'

        if '--server' in args:
            server_addr_flag = '--server'

        server = args[args.index(server_addr_flag) + 1]

        double_dot_index = server.find(':')

        if double_dot_index == -1:
            self.__params['ip'] = server
            self.__params['port'] = 25
        else:
            self.__params['ip'] = server[0:server.find(':')]
            self.__params['port'] = int(server[(server.find(':') + 1):len(server)])

        if '-t' not in args and '--to' not in args:
            print('Не был введен email адрес получателя')
            return dict()

        to_email_flag = '-t'

        if '--to' in args:
            to_email_flag = '--to'

        self.__params['to'] = args[args.index(to_email_flag) + 1]

        self.__params['directory'] = os.getcwd()

        directory_flag = None

        if '-d' in args:
            directory_flag = '-d'

        if '--directory' in args:
            directory_flag = '--directory'

        if directory_flag is not None:
            self.__params['directory'] = args[args.index(directory_flag) + 1]

        if '--ssl' in args:
            self.__params['ssl'] = True

        self.__params['ssl'] = False

        self.__params['from'] = '<>'

        from_email_flag = None

        if '--from' in args:
            from_email_flag = '--from'

        if '-f' in args:
            from_email_flag = '-f'

        if from_email_flag is not None:
            self.__params['from'] = args[args.index(from_email_flag) + 1]

        self.__params['subject'] = 'Happy Pictures'

        if '--subject' in args:
            self.__params['subject'] = args[args.index('--subject') + 1]

        self.__params['auth'] = False

        if '--auth' in args:
            self.__params['auth'] = True

        self.__params['verbose'] = False

        if '-v' in args or '--verbose' in args:
            self.__params['verbose'] = True

    @staticmethod
    def find(name: str) -> int:
        index = -1

        for i in range(0, len(name)):
            if name[i] == '.':
                index = i

        return index

    def send(self, args: list):
        self.__parse_args(args)

        if self.__params.get('help'):
            print(self.__params.get('text'))
            return None

        if self.__params['ssl']:
            self.__smtp_server = smtplib.SMTP_SSL(self.__params.get('ip'), self.__params.get('port'))
        else:
            self.__smtp_server = smtplib.SMTP(self.__params.get('ip'), self.__params.get('port'))

        self.__smtp_server.ehlo()
        self.__smtp_server.starttls()
        self.__smtp_server.ehlo()

        if self.__params['verbose']:
            self.__smtp_server.set_debuglevel(1)

        if self.__params.get('auth'):
            password = getpass.getpass('Пароль: ')

            try:
                self.__smtp_server.login(self.__params['from'], password)
            except smtplib.SMTPException as e:
                print(e)

        multipart_mime = MIMEMultipart()

        multipart_mime['Subject'] = self.__params['subject']
        multipart_mime['From'] = self.__params['from']
        multipart_mime['To'] = self.__params['to']

        for filename in os.listdir(self.__params['directory']):
            path = os.path.join(self.__params['directory'], filename)

            dot_index = self.find(filename)

            if dot_index == -1:
                continue

            ext = filename[(dot_index + 1):len(filename)]

            if (os.path.isfile(path)) and (ext in self.__EXT):
                with open(path, 'rb') as file:
                    image_mime = MIMEImage(file.read())
                    image_mime.add_header('Content-Disposition', 'attachment', filename=filename)
                    multipart_mime.attach(image_mime)

        self.__smtp_server.send_message(multipart_mime)
        self.__smtp_server.close()
