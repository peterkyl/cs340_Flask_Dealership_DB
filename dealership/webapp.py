from flask import Flask, render_template
from flask import request, redirect
from db_connector.db_connector import connect_to_database, execute_query
#create the web application
webapp = Flask(__name__)

@webapp.route('/')
def all_dealerships():
    print("Fetching dealerships and rendering Home page")
    db_connection = connect_to_database()
    query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country, dealership_id FROM dealership INNER JOIN dealership_address USING (address_id);"
    result = execute_query(db_connection, query).fetchall();
    print(result)
    return render_template('home.html', rows=result)

@webapp.route('/selectDealership/<int:dealership_id>')
def select_dealership(dealership_id):
	db_connection = connect_to_database()
	dealership_query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country FROM dealership  INNER JOIN dealership_address USING (address_id) WHERE dealership_id = %s;" % (dealership_id)
	dealership = execute_query(db_connection, dealership_query).fetchall();
	employees_query = "SELECT num_employees, f_name, l_name, position FROM (SELECT COUNT(employee_id) AS num_employees, dealership_id FROM employees WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT f_name, l_name, position, dealership_id FROM employees WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (dealership_id, dealership_id)
	employees = execute_query(db_connection, employees_query).fetchall();
	vehicles_query = "SELECT num_vehicles, vehicle_id, type_name, vin FROM (SELECT vehicle_id, type_name, vin, dealership_id FROM vehicle INNER JOIN vehicle_type ON type=type_id WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT COUNT(vehicle_id) AS num_vehicles, dealership_id FROM vehicle WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (dealership_id, dealership_id)
	vehicles = execute_query(db_connection, vehicles_query).fetchall();
	return render_template('selectDealership.html', employees=employees, vehicles=vehicles, dealership=dealership)

@webapp.route('/addDealership', methods=['POST','GET'])
def add_dealership():
	db_connection = connect_to_database()
	#if request.method == 'GET':
		
	if request.method == 'POST':
		print("Add new dealership!");
		address1 = request.form['address1']
		address2 = request.form['address2']
		city = request.form['city']
		ZIP = request.form['ZIP']
		country = request.form['country']
		hours = request.form['hours']
		dealership_name = request.form['dealership_name']

		address_query = 'INSERT INTO dealership_address (address_line_1, address_line_2, city, zip, country) VALUES (%s,%s,%s,%s,%s)'
		address_data = (address1, address2, city, ZIP, country)
		execute_query(db_connection, address_query, address_data)
		print("inserted address");

		dealership_query = 'INSERT INTO dealership (address_id, dealership_name, hours) VALUES ((SELECT address_id FROM dealership_address WHERE address_line_1 = %s AND address_line_2 = %s AND city = %s AND zip = %s AND country = %s),%s,%s)'
		dealership_data = (address1, address2, city, ZIP, country, dealership_name, hours)
		execute_query(db_connection, dealership_query, dealership_data)
		print("inserted dealership");
		return redirect('/');


###########################################################
### STARTER APP EXAMPLES BELOW

@webapp.route('/add_new_people', methods=['POST','GET'])
def add_new_people():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT planet_id, name from bsg_planets'
        result = execute_query(db_connection, query).fetchall();
        print(result)

        return render_template('people_add_new.html', planets = result)
    elif request.method == 'POST':
        print("Add new people!");
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        query = 'INSERT INTO bsg_people (fname, lname, age, homeworld) VALUES (%s,%s,%s,%s)'
        data = (fname, lname, age, homeworld)
        execute_query(db_connection, query, data)
        return ('Person added!');

@webapp.route('/db-test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from bsg_people;"
    result = execute_query(db_connection, query);
    return render_template('db_test.html', rows=result)

#display update form and process any updates, using the same function
@webapp.route('/update_people/<int:id>', methods=['POST','GET'])
def update_people(id):
    db_connection = connect_to_database()
    #display existing data
    if request.method == 'GET':
        people_query = 'SELECT character_id, fname, lname, homeworld, age from bsg_people WHERE character_id = %s' % (id)
        people_result = execute_query(db_connection, people_query).fetchone()

        if people_result == None:
            return "No such person found!"

        planets_query = 'SELECT planet_id, name from bsg_planets'
        planets_results = execute_query(db_connection, planets_query).fetchall();

        return render_template('people_update.html', planets = planets_results, person = people_result)
    elif request.method == 'POST':
        print("Update people!");
        character_id = request.form['character_id']
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
        homeworld = request.form['homeworld']

        print(request.form);

        query = "UPDATE bsg_people SET fname = %s, lname = %s, age = %s, homeworld = %s WHERE character_id = %s"
        data = (fname, lname, age, homeworld, character_id)
        result = execute_query(db_connection, query, data)
        print(str(result.rowcount) + " row(s) updated");

        return redirect('/browse_bsg_people')

@webapp.route('/delete_people/<int:id>')
def delete_people(id):
    '''deletes a person with the given id'''
    db_connection = connect_to_database()
    query = "DELETE FROM bsg_people WHERE character_id = %s"
    data = (id,)

    result = execute_query(db_connection, query, data)
    return (str(result.rowcount) + "row deleted")
