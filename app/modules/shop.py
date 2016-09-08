# encoding: utf-8
class shop(base):
    def render(self, template_name, **kwargs):
        super(shop, self).render("shop/" + template_name, **kwargs)

class ShopHandler(shop)
	def get(self):
		users = self.db.client().data
		self.render('index.html', users=users)

class NotFoundHandler(shop):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = '/shop'

urls = [
    ('?', ShopHandler),
    ('/1', AjaxHandler),
    ('/2', WebHandler)
]