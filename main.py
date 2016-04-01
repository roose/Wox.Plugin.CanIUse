#encoding=utf8
"""Wox plugin for caniuse.com"""
# import requests moved to get_data func
import os
import time
import json
import collections
from wox import Wox

class CanIUse(Wox):
    """Request data, save, return results by query"""
    abs_path = os.path.dirname(os.path.abspath(__file__))
    data_fn = os.path.join(abs_path, "data.json")

    @staticmethod
    def write_file(filename, data):
        """
        Write file

        :param str filename: filename
        :param str data: data to save
        """
        file_ = open(filename, 'w')
        file_.write(data)
        file_.close()

    @staticmethod
    def read_file(filename):
        """
        Read file

        :param str filename: filename
        :return: file data
        """
        file_ = open(filename, 'r')
        data = file_.read()
        file_.close()
        return data

    @staticmethod
    def browser_version(stats):
        """
        Create supported browser versions string

        :param stats dict: dict with all browser versions
        :return str: supported version
        """
        support = ""
        for (key, val) in stats.items():
            if val.find("a") != -1:
                if support.find("+*") > 0:
                    continue
                support = "".join([key, "+*"])
            elif val.find("y x") != -1:
                if support.find("-px-") > 0:
                    continue
                support = "".join([key, "-px-"])
            elif val == "y":
                support = "".join([key, "+"])
                break

        return support if support else "n/a"

    @staticmethod
    def get_stats(stats):
        """
        Create all browsers feature support in one string

        :param stats dict: dict with all browsers support
        :return str: string with all browser feature support
        """
        data = (stats['FF'], stats['Ch'], stats['S'], stats['IE'])
        text = ", [FF:{0[0]}, CH:{0[1]}, SF:{0[2]}, IE:{0[3]}]".format(data)

        return text

    def get_data(self):
        """
        Get raw data from github/Fyrd/caniuse/master/data.json
        parse it and save to "cache" file
        """
        import requests
        req = requests.get('https://raw.githubusercontent.com/Fyrd/caniuse/master/data.json')
        data = req.json(object_pairs_hook=collections.OrderedDict)
        parsed_data = data['data']
        dct = {}
        for (key, val) in parsed_data.items():
            title = val['title']
            url = "".join(["http://caniuse.com/#feat=", key])
            description = val['description']

            stats = {}
            for (browser, stat) in val['stats'].items():
                stats[browser] = self.browser_version(stat)

            dct[key] = {
                "title":title,
                "url":url,
                "description":description,
                "stats":{
                    "IE":stats['ie'],
                    "FF":stats['firefox'],
                    "Ch":stats['chrome'],
                    "S":stats['safari']
                }
            }

        if len(dct):
            self.write_file(self.data_fn, json.dumps(dct))

    def query(self, key):
        """
        Get query, search in file and return results
        :param str key: query string
        :return: results
        """
        # if file not exists or file is old - create data.json
        if not (os.path.isfile(self.data_fn)) or \
            (os.path.getmtime(self.data_fn) <= int(time.time()-86400*14)):
            self.get_data()

        # read data from file
        data = json.loads(self.read_file(self.data_fn), object_pairs_hook=collections.OrderedDict)
        query = key
        results = []
        bykey = collections.OrderedDict()
        bytitle = collections.OrderedDict()
        bydesc = collections.OrderedDict()

        if query == "":
            results.append({
                "Title": "Search caniuse.com",
                "SubTitle": "Support tables for HTML5, CSS3, etc",
                "IcoPath":"Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "open_url",
                    "parameters":["http://caniuse.com"],
                    "dontHideAfterAction":True
                    }
                })
            return results

        # create result from data
        for (key, result) in data.items():
            value = key.lower().strip()
            title = result['title'].lower().strip()
            description = result['description'].lower().strip()

            if value.find(query) == 0:
                results.append({
                    "Title": "".join([result['title'], self.get_stats(result['stats'])]),
                    "SubTitle": result['description'],
                    "IcoPath":"Images\\caniuse.png",
                    "JsonRPCAction":{
                        "method": "open_url",
                        "parameters":[result['url']],
                        "dontHideAfterAction":False
                        }
                    })
            elif value.find(query) > 0:
                bykey[key] = result
            elif title.find(query) != -1:
                bytitle[key] = result
            elif description.find(query) != -1:
                bydesc[key] = result

        for (key, keyres) in bykey.items():
            results.append({
                "Title": "".join([keyres['title'], self.get_stats(keyres['stats'])]),
                "SubTitle": keyres['description'],
                "IcoPath": "Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "open_url",
                    "parameters":[keyres['url']],
                    "dontHideAfterAction":False
                }
            })

        for (key, titleres) in bytitle.items():
            results.append({
                "Title": "".join([titleres['title'], self.get_stats(titleres['stats'])]),
                "SubTitle": titleres['description'],
                "IcoPath": "Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "open_url",
                    "parameters":[titleres['url']],
                    "dontHideAfterAction":False
                }
            })

        for (key, descres) in bydesc.items():
            results.append({
                "Title": "".join([descres['title'], self.get_stats(descres['stats'])]),
                "SubTitle": descres['description'],
                "IcoPath":"Images\\caniuse.png",
                "JsonRPCAction":{
                    "method": "open_url",
                    "parameters":[descres['url']],
                    "dontHideAfterAction":False
                }
            })

        return results

    def open_url(self, url):
        """
        Function for JsonRPCAction, open url

        :param str url: url to open
        """
        os.startfile(url)

if __name__ == "__main__":
    CanIUse()
