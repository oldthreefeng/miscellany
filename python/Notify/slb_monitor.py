# coding:utf-8
# import aliyunsdkslb
import json,os
from aliyunsdkcore import client
from aliyunsdkslb.request.v20160520 import DescribeLoadBalancersRequest
from aliyunsdkslb.request.v20160520 import DescribeHealthStatusRequest


def get_request(api):
    request = api_mapper.get(api,None)
    if not request:
        raise TypeError,"Undefind api !"
    request.set_accept_format('json')
    return request

def get_slb_activiti():
    result = clt.do_action(get_request('get_all'))
    if 'Code' not in result:
        result = json.loads(result).get('LoadBalancers',{}).get('LoadBalancer',[])

    return filter(lambda s:'activiti' in s['LoadBalancerName'],result)


def slb_check():
    fail_list = []
    slbs_list = get_slb_activiti()
    # print(slbs_list)
    for slb in slbs_list:
        slb_id = slb.get('LoadBalancerId','')
        if not slb_id:
            continue

        # is active ?
        if slb['LoadBalancerStatus'] != 'active':
            slb['err'] = 'SLB {} not active!'
            fail_list.append(slb)

        # is health ?
        request = get_request('get_health')
        request.set_LoadBalancerId(slb_id)
        result = json.loads(clt.do_action(request)).get('BackendServers',{}).get('BackendServer',[])

        for server in result:
            server_status = server.get('ServerHealthStatus','')
            server_id = server.get('ServerId','')
            if server_status != 'normal':
                slb['err'] += 'server {} in SLB {} is down!'.format(server_id,slb_id)

    return None if not fail_list else fail_list


def notify(message):
    print os.popen('python sendWechat.py {}'.format(message)).read()

def main():
    check_result = slb_check()
    check_result = [{"err":"test"}]
    if check_result:
        print('SLB Warning !!')
        n_message = '\n'.join([ e['err'] for e in check_result ])
        notify(n_message)
    else:
        print('ok...')

if __name__ == '__main__':
    AccessKey = 'HJDrwxrAAgA656oi'
    AccessSecret = '5WKBLhwUD8OvqxcZkus3jGUwVmo2je'
    RegionId = 'cn-beijing'
    api_mapper = {
        'get_all' : getattr(DescribeLoadBalancersRequest,'DescribeLoadBalancersRequest')(),
        'get_health' : getattr(DescribeHealthStatusRequest,'DescribeHealthStatusRequest')(),
    }

    clt=client.AcsClient(AccessKey,AccessSecret,RegionId)
    main()
