"""
GANTT Chart with Matplotlib
Sukhbinder
Inspired from
<div class="embed-theclowersgroup"><blockquote class="wp-embedded-content"><a href="http://www.clowersresearch.com/main/gantt-charts-in-matplotlib/">Gantt Charts in Matplotlib</a></blockquote><script type="text/javascript"><!--//--><![CDATA[//><!--        !function(a,b){"use strict";function c(){if(!e){e=!0;var a,c,d,f,g=-1!==navigator.appVersion.indexOf("MSIE 10"),h=!!navigator.userAgent.match(/Trident.*rv:11./),i=b.querySelectorAll("iframe.wp-embedded-content");for(c=0;c<i.length;c++)if(d=i[c],!d.getAttribute("data-secret")){if(f=Math.random().toString(36).substr(2,10),d.src+="#?secret="+f,d.setAttribute("data-secret",f),g||h)a=d.cloneNode(!0),a.removeAttribute("security"),d.parentNode.replaceChild(a,d)}else;}}var d=!1,e=!1;if(b.querySelector)if(a.addEventListener)d=!0;if(a.wp=a.wp||{},!a.wp.receiveEmbedMessage)if(a.wp.receiveEmbedMessage=function(c){var d=c.data;if(d.secret||d.message||d.value)if(!/[^a-zA-Z0-9]/.test(d.secret)){var e,f,g,h,i,j=b.querySelectorAll('iframe[data-secret="'+d.secret+'"]'),k=b.querySelectorAll('blockquote[data-secret="'+d.secret+'"]');for(e=0;e<k.length;e++)k[e].style.display="none";for(e=0;e<j.length;e++)if(f=j[e],c.source===f.contentWindow){if(f.removeAttribute("style"),"height"===d.message){if(g=parseInt(d.value,10),g>1e3)g=1e3;else if(200>~~g)g=200;f.height=g}if("link"===d.message)if(h=b.createElement("a"),i=b.createElement("a"),h.href=f.getAttribute("src"),i.href=d.value,i.host===h.host)if(b.activeElement===f)a.top.location.href=d.value}else;}},d)a.addEventListener("message",a.wp.receiveEmbedMessage,!1),b.addEventListener("DOMContentLoaded",c,!1),a.addEventListener("load",c,!1)}(window,document);//--><!]]></script><iframe sandbox="allow-scripts" security="restricted" src="http://www.clowersresearch.com/main/gantt-charts-in-matplotlib/embed/" width="600" height="338" title="“Gantt Charts in Matplotlib” — The Clowers Group" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" class="wp-embedded-content" kwframeid="1"></iframe></div>
"""
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import WEEKLY,MONTHLY, DateFormatter, rrulewrapper, RRuleLocator
import numpy as np


def _create_date(datetxt):
    """Creates the date"""
    day,month,year=datetxt.split('-')
    date = dt.datetime(int(year), int(month), int(day))
    mdate = matplotlib.dates.date2num(date)
    return mdate

def CreateGanttChart(fname):
    """
        Create gantt charts with matplotlib
        Give file name.
    """
    ylabels = []
    customDates = []
    try:
        textlist=open(fname).readlines()
    except:
        return
#
    for tx in textlist:
        if not tx.startswith('#'):
            ylabel,startdate,enddate=tx.split(',')
            ylabels.append(ylabel.replace('\n',''))
            customDates.append([_create_date(startdate.replace('\n','')),_create_date(enddate.replace('\n',''))])

    ilen=len(ylabels)
    pos = np.arange(0.5,ilen*0.5+0.5,0.5)
    task_dates = {}
    for i,task in enumerate(ylabels):
        task_dates[task] = customDates[i]
    fig = plt.figure(figsize=(20,8))
    ax = fig.add_subplot(111)
    for i in range(len(ylabels)):
         start_date,end_date = task_dates[ylabels[i]]
         ax.barh((i*0.5)+0.5, end_date - start_date, left=start_date, height=0.3, align='center', edgecolor='lightgreen', color='orange', alpha = 0.8)
    locsy, labelsy = plt.yticks(pos,ylabels)
    plt.setp(labelsy, fontsize = 14)
#    ax.axis('tight')
    ax.set_ylim(ymin = -0.1, ymax = ilen*0.5+0.5)
    ax.grid(color = 'g', linestyle = ':')
    ax.xaxis_date()
    rule = rrulewrapper(WEEKLY, interval=1)
    loc = RRuleLocator(rule)
    #formatter = DateFormatter("%d-%b '%y")
    formatter = DateFormatter("%d-%b")

    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    labelsx = ax.get_xticklabels()
    plt.setp(labelsx, rotation=30, fontsize=10)

    font = font_manager.FontProperties(size='small')
    ax.legend(loc=1,prop=font)

    ax.invert_yaxis()
    fig.autofmt_xdate()
    # plt.savefig('gantt.svg')
    plt.show()

if __name__ == '__main__':
    fname=r"projectChart.txt"
    CreateGanttChart(fname)
