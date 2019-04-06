import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="A price is required!"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404          

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400   
        
        data = Item.parser.parse_args()
        
        item = ItemModel(name, data['price']) # need an item model mot dict

        try: 
            item.insert()
        except:
            return {"message": "An error occured inserting the item"}, 500
        
        return item.json(), 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))
        connection.commit()
        connection.close()
        return {'message': 'Item deleted'}
    
    def put(self, name):
        # data = request.get_json()
        # DATA INPUT PARSER !!!
        data = Item.parser.parse_args() # parsed the req and ensured a price is avail
        ## print(data['another']) # if this works then acan use to varify form data

        item = ItemModel.find_by_name(name)
        # updated_item = {'name': name, 'price': data['price']}
        updated_item = ItemModel(name, data['price'])
        if item is None:
            try:
                # ItemModel.insert(updated_item)
                updated_item.insert()
            except:
                return {"message": "An error occured inserting the item"}, 500
        else:
            try:
                # ItemModel.update(updated_item)
                updated_item.update()
            except:
                return {"message": "An error occured updating the item"}, 500
        return updated_item.json()
   

class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'name': row[0], 'price': row[1]})
        
        connection.close()
        return {'items': items}