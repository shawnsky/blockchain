import rsa


class RSA:
    @staticmethod
    def create_keys():
        (pubkey, privkey) = rsa.newkeys(1024)
        pub = pubkey.save_pkcs1()
        with open('public.pem', 'wb+')as f:
            f.write(pub)

        pri = privkey.save_pkcs1()
        with open('private.pem', 'wb+')as f:
            f.write(pri)

    @staticmethod
    def encrypt(text):
        with open('private.pem', 'rb') as privatefile:
            p = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(p)
        original_text = text.encode('utf8')
        crypt_text = rsa.encrypt(original_text, privkey)
        return crypt_text

    @staticmethod
    def decrypt(crypt_text):
        with open('public.pem', 'rb') as publicfile:
            p = publicfile.read()
        pubkey = rsa.PublicKey.load_pkcs1(p)
        lase_text = rsa.decrypt(crypt_text, pubkey).decode()
        print(lase_text)

    @staticmethod
    def get_pk():
        with open('public.pem', 'rb') as publicfile:
            p = publicfile.read()
        return str(p)

