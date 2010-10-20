import StatsIF as SIF
try:
  import json
except:
  import simplejson as json
from RealtimeConfig import config
import re

__bpattern = re.compile("([-]?[\d]+|[-]?inf|)_([-]?[\d]+|inf|)")

def parse_query_string(qstr):
  ret = {}
  items = qstr.split("&");
  for item,val in map(lambda iv: iv.split("="), items):
    ret[item.lower()] = val
  return ret

def parse_bounds_string(boundstr):
  global __bpattern
  ret = []
  minmin = config['min_lateness_minutes']
  maxmax = config['max_lateness_minutes']
  entries = boundstr.lower().split(".")
  for entry in entries:
    groups = __bpattern.match(entry).groups()
    if groups[0] in ("-inf","inf","",None):
      ret.append( (minmin,int(groups[1])) )
    elif groups[1] in ("inf","",None): 
      ret.append( (int(groups[0]),maxmax) )
    else:
      ret.append( (int(groups[0]),int(groups[1])) )
  return ret


class yamwfw(object):
  def handle_error(self,env,start,exc,msg):
    print "ERROR"
    print msg
    start("402 BAD REQUEST", [('','')])
    return None

  def return_json(self,obj):
    return json.dumps(obj);

  def querycall(self,env,start):
    querystr = env['QUERY_STRING']
    values = parse_query_string(querystr)
    try:
      result = self.handle_query(values)
    except Exception, e:
      return self.handle_error(env,start,e,"Invalid request")
    else:
      start( "200 OK", [('Content-type','application/json')] )
      return [ self.return_json(result)+"\n" ]


class GetStops(yamwfw):
  def handle_query(self,values):
    return SIF.get_stops(**values)
  

class GetStopInfo(yamwfw):
  def handle_query(self,values):
    return SIF.get_stop_info(**values)


class GetLatenessStat(yamwfw):
  def handle_query(self,values):
    values['bounds'] = parse_bounds_string(values['bounds'])
    return SIF.get_percentile(**values)


get_stops = GetStops().querycall
get_stop_info = GetStopInfo().querycall
get_lateness_stat = GetLatenessStat().querycall


if __name__=="__main__":
  def start(*args):
    print args
  print get_stops({'QUERY_STRING':
                     "min_lat=37.78&max_lat=37.79&min_lon=-122.40&max_lon=-122.39"}, start)
  print get_stop_info({'QUERY_STRING':
                         'stop_id=6920&dow=0'}, start)
  print get_lateness_stat({'QUERY_STRING':
                             'bounds=_1.-1_.0_1.1_2&trip_id=3955064&stop_seq=10&dow=4'}, start)