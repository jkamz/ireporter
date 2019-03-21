def facebook_share_url(request):
    link = 'http://www.facebook.com/sharer.php?u='+request.data['url']+'&quote=Checkout this ' + request.data['incident_type'] 
    return str(link)

def twitter_share_url(request):
    link = 'https://twitter.com/share?url='+request.data['url']+'&amp;text=Checkout this ' + request.data['incident_type']
    return str(link)

def linkedin_share_url(request):
    link = 'http://www.linkedin.com/shareArticle?url='+request.data['url']+'&title=Checkout this ' + request.data['incident_type'] 
    return str(link)

def mail_share_url(request):
    link = 'mailto:?subject=Checkout this {} read&body={}'.format(request.data['incident_type'], request.data['url'])
    return  str(link)