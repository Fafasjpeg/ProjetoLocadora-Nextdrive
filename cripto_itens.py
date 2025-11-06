from chave_cript import c

class Seguranca:
     def cripto(self,item):
          self.item = item
          if isinstance(self.item,str):
               self.c_item = self.item.encode('utf-8')
          self.c_item = c.encrypt(self.c_item) 
          return self.c_item    

     def descripto(self,item):
          self.d_item = c.decrypt(item)
          return self.d_item.decode()












