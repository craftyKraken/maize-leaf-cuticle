"""Script called remotely by Pi's to render the HTML page listing all the IPs.

Page should display on web at a known url. 

Author: James Chamness
Last modified: May 04, 2017
"""

import jinja2
import os

def loadIPs():
    ips = []
    for i in range(1,7):
        ipFilename = "ip" + str(i) + ".txt"
        ipFilename = "/share/MLC_2017/microclimateMonitors/pipeline/server/" + os.sep + ipFilename    
        with open(ipFilename, 'r') as f:
            ips.append(f.readlines()[0].strip())
    return tuple(ips)

"""Executable"""
if __name__ == "__main__":
    
    ipPageFilename = "/share/MLC_2017/microclimateMonitors/pipeline/server/IP_page.html"
    templateLoader = jinja2.FileSystemLoader(searchpath="/share/MLC_2017/microclimateMonitors/pipeline/server")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templateFilename = "IP_page.jinja"
    template = templateEnv.get_template(templateFilename)
    
    ip1, ip2, ip3, ip4, ip5, ip6 = loadIPs()
    templateVars = { "ip1":ip1, "ip2":ip2, "ip3":ip3, "ip4":ip4, "ip5":ip5, "ip6":ip6 }
    
    outputText = template.render(templateVars)
    outputFile = open(ipPageFilename,'w')
    outputFile.write(outputText)
    outputFile.close()