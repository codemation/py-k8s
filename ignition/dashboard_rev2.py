"""
:Class: Class to Manage the Dashboards using HTTP API

Intialization:


        * title: Title of the Dashboard
        * graphTargets: This parameter will define the number of graphs and the target in every graph using a list
                Example: ( (megastore.stats.encode_bytes, megastore.stats.encode_calls),(CPU_Total_Utilizaiton) )

"""

class Dashboard():

        def __init__(self):

                null = None
                true = True
                false = False
                self.title = ''
                self.url = 'http://10.216.35.215/api/dashboards/db'
                self.fromdate = 'now-30d'
                        #"2018-01-01T01:16:33.186Z"
                self.todate = 'now'
                        #"2018-01-01T21:07:03.490Z"
                self.graphTargets = [[]]
                self.authorizationkey = 'Bearer eyJrIjoiM1BGcmRvWEUyR21uUm1ET0NqaVA5VnNIaWE3ZE1ISjMiLCJuIjoiYWRtaW4iLCJpZCI6MX0='

                self.numberRows = -1
                self.rows = []
                self.panels = []

                self.dashboard = {
                        "dashboard": {
                                "id": null,
                                "title": "No Title",
                                "tags": [],
                                "templating": {
                                        "list": []
                                },
                                "time": {
                                        "from": "now-30d",
                                        "to": "now"
                                },
                                "timezone": "browser",
                                "rows": [],
                                "schemaVersion": 14,
                                "version": 0
                        },
                        "overwrite": false
                }

        def addTitle(self,title):
                self.title = title
                self.deleteDashboard(self.title)
                
                self.dashboard['dashboard']["title"] = '{}'.format(title)

        def addGraphsTargets(self,graphtargets):

                import copy
                self.graphTargets = copy.deepcopy(graphtargets)
                print ("Dashboard GraphTargets_after copy.deepcopy %s" %(self.graphTargets))

        def createDashboard(self):

                tc = 0

                #print('Targets in dasboard are: {}'.format(self.graphTargets))
                
                """rows - iterates through input after deep-copy"""
                for rows in self.graphTargets:
                    for key in rows:
                        panel = self.createPanel(key,self.numberRows+1, rows[key]['Format'], rows[key]['YAxisLogBase'])
                        #print ('New Panel is:{}'.format(panel))
                        row = self.createRow('Test')
                        #print ('New Row is:{}'.format(row))

                        self.panels.append(panel)
                        self.rows.append(row)
                        self.numberRows = self.numberRows + 1
                        count = 1
                        print ("createDashboard: %s Starting to append items " %(key))
                        for targetpath in rows[key]['items']:
                                #print ('Going to insert targetpath: {}'.format(targetpath))
                                print ("createDashboard: CreateTarget Called for %s " %(targetpath))
                                target = self.createTarget(count,targetpath)
                                #print ('Target: {}'.format(target))
                                #print('Temp Count is: {}'.format(tc))
                                self.panels[tc]['targets'].append(target)
                                #self.panels[tc]["yaxes"][0]["format"] = rows[key]['Format']
                                #self.panels[tc]["yaxes"][0]["logBase"] = rows[key]['YAxisLogBase']
                                count+=1
                                #print ('Self Panel is: {}'.format(self.panels))
                        tc += 1
                print ("Create DashBoard - rows - iterates through input after deep-copy: Completed")
                temp_count = 0

                for panel in self.panels:
                        self.rows[temp_count]['panels'].append(panel)
                        temp_count +=1
                print ("Create DashBoard - PANELS - panels appened")
                temp_count = 0

                for row in self.rows:
                       self.dashboard['dashboard']['rows'].append(row)
                print ("Create DashBoard - rows - rows appened")

        def createPanel(self,panelTitle,panelId, YUnit, YLogArithView):

                null = None
                true = True
                false = False

                panel=  {
                        "aliasColors": {},
                        "bars": false,
                        "datasource": "Test",
                        "description": null,
                        "editable": true,
                        "error": false,
                        "fill": 1,
                        "id": panelId,
                        "isNew": true,
                        "legend": {
                                "avg": false,
                                "current": false,
                                "max": true,
                                "min": true,
                                "show": true,
                                "total": false,
                                "values": false
                        },
                        "lines": true,
                        "linewidth": 2,
                        "nullPointMode": "connected",
                        "percentage": false,
                        "pointradius": 5,
                        "points": false,
                        "renderer": "flot",
                        "seriesOverrides": [],
                        "span": 12,
                        "stack": false,
                        "steppedLine": false,
                        "targets": [],
                        "timeFrom": null,
                        "timeShift": null,
                        "title": str(panelTitle),
                        "tooltip": {
                                "shared": true,
                                "sort": 0,
                                "value_type": "individual"
                        },
                        "type": "graph",
                        "xaxis": {
                                "show": true,
                                "mode": "time",
                                "name": null,
                                "show": true,
                                "values": []
                        },
                        "yaxes": [
                                {       "decimals": null,
                                        "format": YUnit,
                                        "label": null,
                                        "logBase": int(YLogArithView),
                                        "max": null,
                                        "min": 0,
                                        "show": true
                                },
                                {
                                        "format": "short",
                                        "label": null,
                                        "logBase": 1,
                                        "max": null,
                                        "min": null,
                                        "show": true
                                }
                        ]
                }
                return panel

        def createRow(self,rowTitle):
                
            
                test = {1: 'test'}
                null = None
                true = True
                false = False
                row = {
                        "repeat": null,
                        "showTitle": false,
                        "title": "Title",
                        "collapse": false,
                        "editable": true,
                        "height": "250px",
                        "panels": []
                }

                return row

        def createTarget(self,count,path):
                indexd = {
                          1: "A",  
                          2: "B", 
                          3: "C", 
                          4: "D", 
                          5: "E", 
                          6: "F", 
                          7: "G", 
                          8: "H", 
                          9: "I", 
                          10: "J", 
                          11: "K",  
                          13: "L",
                          14: "M",
                          15: "N",
                          16: "O",
                          17: "P",
                          18: "Q",
                          19: "R",
                          20: "S",
                          21: "T",
                          22: "U",
                          23: "V",
                          24: "W",
                          25: "X",
                          26: "Y",
                          27: "Z"}
                if not count in indexd:
                    print ("Cannot add more targets, use a smaller query!")
                    return
                target = {
                        "refId": indexd[count],
                        "target": "{}".format(path)
                }
                print ("Completed")
                return target

        def sendHTTPAPI(self):

                import requests
                import json

                headers = {
                        'Accept': 'application/json',
                        'Content-type': 'application/json',
                        'Authorization': '{}'.format(self.authorizationkey)}

                response = requests.post(self.url, data=json.dumps(self.dashboard), headers=headers)
                print response
                return response

        def deleteDashboard(self,name):

                import requests
                import json

                
                url = 'http://10.216.35.215/api/dashboards/db/{}'.format(name.lower())

                headers = {
                        'Accept': 'application/json',
                        'Content-type': 'application/json',
                        'Authorization': '{}'.format(self.authorizationkey)}

                response = requests.delete(url, data=json.dumps(self.dashboard), headers=headers)
                print ("Delete Dashboard URL: %s" %(url))
                print ("Delete Dashboard response: %s" %(response))
                return response
