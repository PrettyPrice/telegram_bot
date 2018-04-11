from price_parser import tmp_geting_data
class Basket:

    def __init__(self, chat_id):
        self.basket_list = []
        self.chat_id = chat_id
        self.counter = 0
        self.barcode_list = []

    def incr_counter(self):
        self.counter += 1

    def add_barcode_to_list(self, barcode):
        self.barcode_list.append(barcode)
    def add(self, item):
        self.basket_list.append(item)

    def __str__(self):
        return str(self.basket_list)

    def check_basket(self):
        print(self.counter)
        products_names = [item['product_name'] for item in self.basket_list]
        print(len(products_names))
        if self.counter == len(products_names):
            return True

    @staticmethod
    def get_result_with_barcode(barcode_list):
        product_list = []
        for barcode in barcode_list:
            tmp = tmp_geting_data(barcode)
            product_list.append(tmp)

        result = {}
        for item in product_list:
            for shop in item['price_list']:
                result[shop['name']] = 0
        # print(self.basket_list)
        for item in product_list:
            for shop in item['price_list']:
                if shop['price'] == 'немає в наявності' or result[shop['name']] == 'Деякого товару немає в наявності':
                    result[shop['name']] = 'Деякого товару немає в наявності'
                else:
                    result[shop['name']] += float(shop['price'])
        # print(result)
        products_names = [item['product_name'] for item in product_list]
        # print(products_names)
        products = [i[17:-14] for i in products_names]
        tmp = ', '.join(products)
        res_str = 'Ціни на обрану корзину: (' + tmp + ')' + '\n'
        for name, price in result.items():
            if type(price) != str:
                res_str += name + ' - ' + '%.2f' % price + '\n'
            else:
                res_str += name + ' - ' + price + '\n'
        return res_str

    def get_result(self):
        result = {}
        for item in self.basket_list:
            for shop in item['price_list']:
                result[shop['name']] = 0
        # print(self.basket_list)
        for item in self.basket_list:
            for shop in item['price_list']:
                if shop['price'] == 'немає в наявності' or result[shop['name']] == 'Деякого товару немає в наявності':
                    result[shop['name']] = 'Деякого товару немає в наявності'
                else:
                    result[shop['name']] += float(shop['price'])
        # print(result)
        products_names = [item['product_name'] for item in self.basket_list]
        # print(products_names)
        products =[i[17:-14] for i in products_names]
        tmp = ', '.join(products)
        res_str = 'Ціни на обрану корзину: (' + tmp + ')' +'\n'
        for name, price in result.items():
            if type(price) != str:
                res_str += name + ' - ' + '%.2f' % price + '\n'
            else:
                res_str += name + ' - ' + price + '\n'
        return res_str
    def clear_basket(self):
        self.basket_list = []

