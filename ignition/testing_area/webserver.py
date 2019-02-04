import web
from htmlform import button,form
from htmlpage import page

urls = ('/', 'Home',
        '/addboot/(.*)', 'AddCss',
        '/NewSession', 'NewSession',
        '/Admin', 'Admin')

class Home:
    def GET(self):
        aPage = page("Home")
        aButton = button('Home', name="Home", value="Home")
        aForm = form("Home", items=[aButton], options=['action=/'])
        return aPage.htmlrender(aForm)
    def POST(self):
        aPage = page("Home")
        aButton = button('Home', name="Home", value="Home")
        aForm = form("Home", items=[aButton], options=['action=/'])
        return aPage.htmlrender(aForm)
class AddCss:
    def GET(self, target):
        aPage = page(target)
        aPage.head.add_link('<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">')
        aPage.save()
        aButton = button(target, name=target, value=target)
        aForm = form(target, items=[aButton], options=['action=/'])
        return aPage.htmlrender(aForm)


if __name__ == "__main__":
    app = web.application(urls,globals())
    app.run()

