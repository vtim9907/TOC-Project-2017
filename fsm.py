from transitions.extensions import GraphMachine

import xml.etree.ElementTree as ET
import urllib.request
import apiai
import json

WEATHER_API_KEY = 'WEATHER_API_KEY'
weather_response = urllib.request.urlopen('http://opendata.cwb.gov.tw/opendataapi?dataid=F-C0032-001&authorizationkey=' + WEATHER_API_KEY)
air_respons = urllib.request.urlopen('http://opendata.epa.gov.tw/ws/Data/REWXQA/?%24orderby=SiteName&%24skip=0&%24top=1000&format=xml')
uv_response = urllib.request.urlopen('http://opendata.epa.gov.tw/ws/Data/UV/?format=xml')

weather_tree = ET.parse(weather_response).getroot()
air_tree = ET.parse(air_respons).getroot()
uv_tree = ET.parse(uv_response).getroot()

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def default_query(self, update):
        text = update.message.text
        return 1

    def weather_query(self, update):
        ptxt = intent_parser(update.message.text)
        text = ptxt['result']['fulfillment']['speech']
        print(ptxt)
        return text == '天氣'

    def weather_city_query(self, update):
        text = update.message.text
        return 1

    def air_query(self, update):
        ptxt = intent_parser(update.message.text)
        text = ptxt['result']['fulfillment']['speech']
        print(ptxt)
        return text == '空氣'

    def air_city_query(self, update):
        text = update.message.text
        return 1

    def uv_query(self, update):
        ptxt = intent_parser(update.message.text)
        text = ptxt['result']['fulfillment']['speech']
        print(ptxt)
        return text == '紫外線'

    def uv_city_query(self, update):
        text = update.message.text
        return 1

    def uvi_query(self, update):
        ptxt = intent_parser(update.message.text)
        text = ptxt['result']['fulfillment']['speech']
        return text == 'uvi'

    def on_enter_state1(self, update):
        update.message.reply_text("你好～ 可以問我目前的 天氣狀況、空氣狀況、或紫外線情形喔！\n你想知道些什麼呢～？\n\n(e.g. 今天天氣如何？)")
        self.go_back(update)

    def on_exit_state1(self, update):
        print('Leaving state1')

    def on_enter_state2(self, update):
        update.message.reply_text("你想知道目前哪個縣市的天氣狀況呢？\n(e.g. 臺南市)")
        #self.go_back(update)

    def on_exit_state2(self, update):
        print('Leaving state2')

    def on_enter_state3(self, update):
        ptxt = intent_parser(update.message.text)
        #text = ptxt['result']['parameters']['Taiwan-city']
        print(ptxt)
        if ptxt['result']['fulfillment']['speech'] != '你在說啥':
            for location in weather_tree.findall('.//{urn:cwb:gov:tw:cwbcommon:0.1}location'):
                if ptxt['result']['parameters']['Taiwan-city'] in location[0].text:
                    update.message.reply_text('%s目前的天氣為%s。\n' \
                    '溫度為 %s 至 %s ℃，降雨機率為 %s %%。' \
                    % (location[0].text, location[1][1][2][0].text,
                        location[3][1][2][0].text, location[2][1][2][0].text,
                        location[5][1][2][0].text))
                    break
        else:
            for location in weather_tree.findall('.//{urn:cwb:gov:tw:cwbcommon:0.1}location'):
                if '臺南市' in location[0].text:
                    update.message.reply_text('對不起，無法辨識您想查詢的是哪個城市，\n為您查詢臺南市的空氣資訊：\n%s目前的天氣為%s。\n' \
                    '溫度為 %s 至 %s ℃，降雨機率為 %s %%。' \
                    % (location[0].text, location[1][1][2][0].text,
                        location[3][1][2][0].text, location[2][1][2][0].text,
                        location[5][1][2][0].text))
                    break
        self.go_back(update)

    def on_exit_state3(self, update):
        print('Leaving state3')

    def on_enter_state4(self, update):
        update.message.reply_text("你想知道目前哪個縣市的空氣狀況呢？\n(e.g. 臺南市)")

    def on_exit_state4(self, update):
        print('Leaving state4')

    def on_enter_state5(self, update):
        ptxt = intent_parser(update.message.text)
        if ptxt['result']['fulfillment']['speech'] != '你在說啥':
            for data in air_tree.findall('./Data'):
                if ptxt['result']['parameters']['Taiwan-city'] in data[1].text:
                    update.message.reply_text('%s目前空氣品質%s！\n一氧化碳濃度(CO)：%s\n' \
                        '臭氧濃度(O3)：%s\n二氧化氮濃度(NO2)：%s\n懸浮微粒濃度(PM10)：%s\n' \
                        '細懸浮微粒濃度(PM2.5)：%s\n' \
                        % (data[1].text, data[4].text, data[6].text, data[7].text,
                        data[10].text, data[8].text, data[9].text))
                    break
        else:
            for data in air_tree.findall('./Data'):
                if '臺南市' in data[1].text:
                    update.message.reply_text('對不起，無法辨識您想查詢的是哪個城市，\n為您查詢臺南市的空氣資訊：\n%s目前空氣品質%s！\n一氧化碳濃度(CO)：%s\n' \
                        '臭氧濃度(O3)：%s\n二氧化氮濃度(NO2)：%s\n懸浮微粒濃度(PM10)：%s\n' \
                        '細懸浮微粒濃度(PM2.5)：%s\n' \
                        % (data[1].text, data[4].text, data[6].text, data[7].text,
                           data[10].text, data[8].text, data[9].text))
                    break
        self.go_back(update)

    def on_exit_state5(self, update):
        print('Leaving state5')

    def on_enter_state6(self, update):
        update.message.reply_text("你想知道目前哪個縣市的紫外線狀況呢？\n(e.g. 臺南市)")

    def on_exit_state6(self, update):
        print('Leaving state6')

    def on_enter_state7(self, update):
        ptxt = intent_parser(update.message.text)
        if ptxt['result']['fulfillment']['speech'] != '你在說啥':
            for data in uv_tree.findall('./Data'):
                if ptxt['result']['parameters']['Taiwan-city'] in data[3].text:
                    if int(data[1].text) <= 2:
                        update.message.reply_text('%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於弱等級，基本上不須要保護措施！\n可以安心外出，但請留意瞬間紫外線。\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    elif int(data[1].text) <= 7:
                        update.message.reply_text('%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於中、強等級！需要保護措施！\n外出時，請盡量待在陰涼處，並使用長袖衣物、帽子、陽傘、防曬乳、太陽眼鏡作為保護！\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    else:
                        update.message.reply_text('%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於極強、危險等級！必須要保護措施！！\n上午 10 點至下午 2 點最好不要外出！盡量待在室內，並使用帽子、陽傘、防曬乳、太陽眼鏡作為保護！\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    break
        else:
            for data in uv_tree.findall('./Data'):
                if '臺南市' in data[3].text:
                    if int(data[1].text) <= 2.0:
                        update.message.reply_text('對不起，無法辨識您想查詢的是哪個城市，\n為您查詢臺南市的空氣資訊：\n\n%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於弱等級，基本上不須要保護措施！\n可以安心外出，但請留意瞬間紫外線。\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    elif int(data[1].text) <= 7.0:
                        update.message.reply_text('對不起，無法辨識您想查詢的是哪個城市，\n為您查詢臺南市的空氣資訊：\n\n%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於中、強等級！需要保護措施！\n外出時，請盡量待在陰涼處，並使用長袖衣物、帽子、陽傘、防曬乳、太陽眼鏡作為保護！\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    else:
                        update.message.reply_text('對不起，無法辨識您想查詢的是哪個城市，\n為您查詢臺南市的空氣資訊：\n\n%s目前紫外線氣象指標(UVI)為 %s。\n目前 UVI 屬於極強、危險等級！必須要保護措施！！\n上午 10 點至下午 2 點最好不要外出！盡量待在室內，並使用帽子、陽傘、防曬乳、太陽眼鏡作為保護！\n\np.s. 如果不清楚紫外線氣象指標(UVI)是什麼的話，也可以問我喔～！' \
                            % (data[3].text, data[1].text))
                    break
        self.go_back(update)

    def on_exit_state7(self, update):
        print('Leaving state7')

    def on_enter_state8(self, update):
        update.message.reply_text("UVI (Ultraviolet INDEX)由世界衛生組織(WHO)、聯合國環境組織、世界氣象組織…等所開發所制定的標準，氣象上用來表示紫外線照射的安全範圍，避免過度暴露於紫外線而產生病變。1994年世界氣象組織向世界各國推廣紫外線指標，UVI被公認為無形的紫外傷害的最佳指標。UVI數值越高，表示潛在的危險越高，因採取避可能對皮膚和眼睛的傷害。")
        update.message.reply_photo("https://drive.google.com/open?id=0B5U04sdfA2_1Y1VxT1c3d1BzQk0")
        self.go_back(update)

    def on_exit_state8(self, update):
        print('Leaving state8')

def intent_parser(input):
    client = apiai.ApiAI('3963ac09560347289b24325bad76401a')

    request = client.text_request()
    request.query = input

    response = request.getresponse()
    return json.loads(response.read().decode())