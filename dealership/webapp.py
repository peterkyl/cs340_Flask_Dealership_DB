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

	employees_query = "SELECT num_employees, f_name, l_name, position, employee_id FROM (SELECT COUNT(employee_id) AS num_employees, dealership_id FROM employees WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT f_name, l_name, position, employee_id, dealership_id FROM employees WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (dealership_id, dealership_id)
	employees = execute_query(db_connection, employees_query).fetchall();

	vehicles_query = "SELECT num_vehicles, vehicle_id, type_name, vin FROM (SELECT vehicle_id, type_name, vin, dealership_id FROM vehicle INNER JOIN vehicle_type ON type=type_id WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT COUNT(vehicle_id) AS num_vehicles, dealership_id FROM vehicle WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (dealership_id, dealership_id)
	vehicles = execute_query(db_connection, vehicles_query).fetchall();

	types_query = 'SELECT type_name FROM vehicle_type'
	types = execute_query(db_connection, types_query).fetchall();
	return render_template('selectDealership.html', employees=employees, vehicles=vehicles, dealership=dealership, dealership_id = dealership_id, types=types)


@webapp.route('/selectVehicle/<int:dealership_id>/<int:vehicle_id>')
def select_vehicle(dealership_id, vehicle_id):
	db_connection = connect_to_database()
	dealership_query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country FROM dealership  INNER JOIN dealership_address USING (address_id) WHERE dealership_id = %s;" % (dealership_id)
	dealership = execute_query(db_connection, dealership_query).fetchall();

	num_emp_query = "SELECT COUNT(employee_id) FROM employees WHERE dealership_id = %s" % (dealership_id)
	num_emp = execute_query(db_connection, num_emp_query).fetchall();

	vehicles_query = "SELECT num_vehicles, vehicle_id, type_name, vin FROM (SELECT vehicle_id, type_name, vin, dealership_id FROM vehicle INNER JOIN vehicle_type ON type=type_id WHERE vehicle_id = %s) AS tabl1 INNER JOIN (SELECT COUNT(vehicle_id) AS num_vehicles, dealership_id FROM vehicle WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (vehicle_id, dealership_id)
	vehicles = execute_query(db_connection, vehicles_query).fetchall();

	features_query = "SELECT feature_name, feature_value, feature_description, feature_id FROM vehicle INNER JOIN vehicle_feature USING (vehicle_id) INNER JOIN feature USING (feature_id) WHERE vehicle_id = %s" % (vehicle_id)
	features = execute_query(db_connection, features_query).fetchall();

	allfeatures_query = "SELECT feature_id, feature_name, feature_description FROM feature"
	allfeatures = execute_query(db_connection, allfeatures_query).fetchall();

	return render_template('selectVehicle.html', dealership=dealership, dealership_id=dealership_id, employees=num_emp, vehicles=vehicles, features=features, allfeatures=allfeatures)

### ADD ROUTES

@webapp.route('/addDealership', methods=['POST'])
def add_dealership():
	db_connection = connect_to_database()
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
	return redirect('/')


@webapp.route('/addEmployee/<int:dealership_id>', methods=['POST'])
def add_employee(dealership_id):
	db_connection = connect_to_database()
	print("Add new employee!")
	fname = request.form['fname']
	lname = request.form['lname']
	position = request.form['position']
	employee_query = 'INSERT INTO employees (dealership_id, f_name, l_name, position) VALUES (%s, %s, %s, %s)'
	employee_data = (dealership_id, fname, lname, position)
	execute_query(db_connection, employee_query, employee_data)
	print("inserted employee")
	return redirect('selectDealership/' + str(dealership_id))


@webapp.route('/addVehicle/<int:dealership_id>', methods=['POST'])
def add_vehicle(dealership_id):
	db_connection = connect_to_database()
	print("Add new vehicle!")
	veh_type = request.form['type']
	vin = request.form['vin']

	#add type to table if new
	types_query = "INSERT IGNORE INTO vehicle_type (type_name) VALUES (%s)"
	types_data = (veh_type)
	execute_query(db_connection, types_query, [types_data])
	type_id_query = "SELECT type_id FROM vehicle_type WHERE type_name = %s"
	type_id = execute_query(db_connection, type_id_query, [types_data]).fetchone();
	print("type insert complete")

	vehicle_query = "INSERT INTO vehicle (dealership_id, type, vin) VALUES (%s, %s, %s)"
	vehicle_data = (dealership_id, type_id, vin)
	print(vehicle_data)
	execute_query(db_connection, vehicle_query, vehicle_data)

#ADD FEATURES???

	print("inserted vehicle")
	return redirect('selectDealership/' + str(dealership_id))


@webapp.route('/addExistingFeature/<int:dealership_id>/<int:vehicle_id>', methods=['POST'])
def add_existing_feature(dealership_id, vehicle_id):
	db_connection = connect_to_database();
	feature_id = request.form['existing_feature']
	feature_value = request.form['existing_value']
	vehicle_feature_query = 'INSERT INTO vehicle_feature (vehicle_id, feature_id, feature_value) VALUES (%s, %s, %s)'
	feature_data = (vehicle_id, feature_id, feature_value)
	execute_query(db_connection, vehicle_feature_query, feature_data)
	return redirect('selectVehicle/' + str(dealership_id) + '/' + str(vehicle_id))


@webapp.route('/addNewFeature/<int:dealership_id>/<int:vehicle_id>', methods=['POST'])
def add_new_feature(dealership_id, vehicle_id):
	db_connection = connect_to_database();
	feature_name = request.form['new_feature']
	feature_description = request.form['new_description']
	feature_value = request.form['new_value']
	feature_query = 'INSERT INTO feature (feature_name, feature_description) VALUES (%s, %s)'
	feature_data = (feature_name, feature_description)
	execute_query(db_connection, feature_query, feature_data)
	vehicle_feature_query = 'INSERT INTO vehicle_feature (vehicle_id, feature_id, feature_value) VALUES (%s,LAST_INSERT_ID(),%s)'
	vehicle_feature_data = (vehicle_id, feature_value)
	execute_query(db_connection, vehicle_feature_query, vehicle_feature_data)
	return redirect('selectVehicle/' + str(dealership_id) + '/' + str(vehicle_id))
	
### DELETE ROUTES

@webapp.route('/deleteDealership/<int:dealership_id>')
def delete_dealership(dealership_id):
	db_connection = connect_to_database();
	query = "DELETE dealership, dealership_address FROM dealership INNER JOIN dealership_address USING (address_id) WHERE dealership_id = %s"
	data = (dealership_id,)
	result = execute_query(db_connection, query, data)
	return redirect('/')

@webapp.route('/deleteEmployee/<int:dealership_id>/<int:employee_id>')
def delete_employee(dealership_id, employee_id):
	db_connection = connect_to_database();
	query = "DELETE FROM employees WHERE employee_id = %s"
	data = (employee_id,)
	result = execute_query(db_connection, query, data)
	return redirect('selectDealership/' + str(dealership_id))

@webapp.route('/deleteVehicle/<int:dealership_id>/<int:vehicle_id>')
def delete_vehicle(dealership_id, vehicle_id):
	db_connection = connect_to_database();
	query = "DELETE FROM vehicle WHERE vehicle_id = %s"
	data = (vehicle_id,)
	result = execute_query(db_connection, query, data)
	return redirect('selectDealership/' + str(dealership_id))

@webapp.route('/deleteFeature/<int:dealership_id>/<int:vehicle_id>/<int:feature_id>')
def delete_feature(dealership_id, vehicle_id, feature_id):
	db_connection = connect_to_database();
	query = "DELETE FROM vehicle_feature WHERE vehicle_id = %s AND feature_id = %s"
	data = (vehicle_id, feature_id)
	result = execute_query(db_connection, query, data)
	return redirect('selectVehicle/' + str(dealership_id) + '/' + str(vehicle_id))




##############################################################
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
