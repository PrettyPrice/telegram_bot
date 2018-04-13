import requests


class Listex:

    def __init__(self, api_key):
        self.api_key = api_key
        self.url = 'https://api.listex.info/v3/'

    def get_product_info(self, barcode=None, product_name=None):
        request_url = self.url + 'product?apikey='+ self.api_key + '&gtin=' + str(barcode)
        response = requests.get(request_url, auth=())
        self.respone_json = response.json()
        return response.json()


    def get_product_name(self):

        good_atrrs = self.respone_json['result'][0]['good_attrs']

        for attr in good_atrrs:
            if attr['attr_group_name'] == 'Название товара' and attr['attr_name'] == 'Краткое название (укр.)':
                result = 'Назва' + ' : ' + attr['attr_value']
                return result

    def get_product_barcode(self):
        result = self.respone_json['result'][0]['identified_by'][0]['value']
        return result

    def get_pr_img_url(self):
        result = self.respone_json['result'][0]['good_img']
        return result

    def get_cat_name(self):
        result = self.respone_json['result'][0]['categories'][0]['cat_name']
        return result

    def get_brand_name(self):
        result = self.respone_json['result'][0]['brand_name']
        return result

    def get_avg_price(self):
        result = self.respone_json['result'][0]['good_avg_price']

        if result is None:
            result = 'не відомо'

        return str(result)

    def get_pr_rating(self):
        result = self.respone_json['result'][0]['good_rating']
        if result is None:
            result = 'не відомо'
        return result

    def get_nutritional_charct(self):
        good_atrrs = self.respone_json['result'][0]['good_attrs']
        attrs = {}
        for attr in good_atrrs:
            if attr['attr_group_name'] == 'Питательные характеристики':
                attrs[attr['attr_name']] = attr['attr_value']
        return attrs

    def get_main_charct(self):
        good_atrrs = self.respone_json['result'][0]['good_attrs']
        attrs = {}
        for attr in good_atrrs:
            if attr['attr_group_name'] == 'Основные':
                attrs[attr['attr_name']] = attr['attr_value']

    def get_composition(self):
        good_atrrs = self.respone_json['result'][0]['good_attrs']
        result = ''
        for attr in good_atrrs:
            if attr['attr_group_name'] == 'Состав товара' and attr['attr_name'] == 'Состав (укр.)':
                result = 'Cклад : ' + attr['attr_value']
        return result


# l = Listex('7c7lrxg9q2y25mf')
# l.get_product_info('4820000455732')
#
# print(l.get_cat_name())


