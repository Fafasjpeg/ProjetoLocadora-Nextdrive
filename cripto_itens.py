import bcrypt

class Seguranca:
    @staticmethod
    def gerar_hash(senha: str) -> str:
        # gera um hash da senha usando bcrypt
        senha_bytes = senha.encode()
        salt = bcrypt.gensalt()
        hash_final = bcrypt.hashpw(senha_bytes, salt)
        return hash_final.decode()  # salva no banco como string hashada

    @staticmethod
    def verificar(senha_digitada: str, hash_banco: str) -> bool:
        # compara a senha digitada com o hash salvo no banco
        return bcrypt.checkpw(senha_digitada.encode(), hash_banco.encode())