from flask import Flask, render_template
from flask import request, redirect
from db_connector.db_connector import connect_to_database, execute_query
#create the web application
webapp = Flask(__name__)

@webapp.route('/', methods=['GET','POST'])
def all_dealerships():
	db_connection = connect_to_database();
	search = ''
	if request.method == 'POST':
		search = request.form['search']
	query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country, dealership_id FROM dealership INNER JOIN dealership_address USING (address_id) WHERE INSTR(dealership_name, '%s')" % (search)
	result = execute_query(db_connection, query).fetchall();
	return render_template('home.html', rows=result)


@webapp.route('/selectDealership/<int:dealership_id>', methods=['GET', 'POST'])
def select_dealership(dealership_id):
	db_connection = connect_to_database();
	search_emp = ''
	search_veh = ''
	if request.method == 'POST':
		if 'search_emp' in request.form:
			search_emp = request.form['search_emp']
		if 'search_veh' in request.form:
			search_veh = request.form['search_veh']
	dealership_query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country FROM dealership  INNER JOIN dealership_address USING (address_id) WHERE dealership_id = %s;" % (dealership_id)
	dealership = execute_query(db_connection, dealership_query).fetchall();

	employees_query = "SELECT num_employees, f_name, l_name, position, employee_id FROM (SELECT COUNT(employee_id) AS num_employees, dealership_id FROM employees WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT f_name, l_name, position, employee_id, dealership_id FROM employees WHERE dealership_id = %s) AS tabl2 USING (dealership_id) WHERE INSTR(f_name, '%s') OR INSTR(l_name, '%s');" % (dealership_id, dealership_id, search_emp, search_emp)
	employees = execute_query(db_connection, employees_query).fetchall();

	vehicles_query = "SELECT num_vehicles, vehicle_id, type_name, vin FROM (SELECT vehicle_id, type_name, vin, dealership_id FROM vehicle INNER JOIN vehicle_type ON type=type_id WHERE dealership_id = %s) AS tabl1 INNER JOIN (SELECT COUNT(vehicle_id) AS num_vehicles, dealership_id FROM vehicle WHERE dealership_id = %s) AS tabl2 USING (dealership_id) WHERE INSTR(vin, '%s');" % (dealership_id, dealership_id, search_veh)
	vehicles = execute_query(db_connection, vehicles_query).fetchall();

	types_query = 'SELECT type_name FROM vehicle_type'
	types = execute_query(db_connection, types_query).fetchall();
	return render_template('selectDealership.html', employees=employees, vehicles=vehicles, dealership=dealership, dealership_id = dealership_id, types=types)


@webapp.route('/selectVehicle/<int:dealership_id>/<int:vehicle_id>', methods=['Get', 'POST'])
def select_vehicle(dealership_id, vehicle_id):
	db_connection = connect_to_database();
	search = ''
	if request.method == 'POST':
		search = request.form['search']
	dealership_query = "SELECT dealership_name, hours, address_line_1, address_line_2, city, zip, country FROM dealership  INNER JOIN dealership_address USING (address_id) WHERE dealership_id = %s;" % (dealership_id)
	dealership = execute_query(db_connection, dealership_query).fetchall();

	num_emp_query = "SELECT COUNT(employee_id) FROM employees WHERE dealership_id = %s" % (dealership_id)
	num_emp = execute_query(db_connection, num_emp_query).fetchall();

	vehicles_query = "SELECT num_vehicles, vehicle_id, type_name, vin FROM (SELECT vehicle_id, type_name, vin, dealership_id FROM vehicle INNER JOIN vehicle_type ON type=type_id WHERE vehicle_id = %s) AS tabl1 INNER JOIN (SELECT COUNT(vehicle_id) AS num_vehicles, dealership_id FROM vehicle WHERE dealership_id = %s) AS tabl2 USING (dealership_id);" % (vehicle_id, dealership_id)
	vehicles = execute_query(db_connection, vehicles_query).fetchall();

	features_query = "SELECT feature_name, feature_value, feature_description, feature_id FROM vehicle INNER JOIN vehicle_feature USING (vehicle_id) INNER JOIN feature USING (feature_id) WHERE vehicle_id = %s AND INSTR(feature_name, '%s')" % (vehicle_id, search)
	features = execute_query(db_connection, features_query).fetchall();

	allfeatures_query = "SELECT feature_id, feature_name, feature_description FROM feature"
	allfeatures = execute_query(db_connection, allfeatures_query).fetchall();

	return render_template('selectVehicle.html', dealership=dealership, dealership_id=dealership_id, employees=num_emp, vehicles=vehicles, features=features, allfeatures=allfeatures)

### ADD ROUTES

@webapp.route('/addDealership', methods=['POST'])
def add_dealership():
	db_connection = connect_to_database();
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

	dealership_query = 'INSERT INTO dealership (address_id, dealership_name, hours) VALUES ((SELECT address_id FROM dealership_address WHERE address_line_1 = %s AND address_line_2 = %s AND city = %s AND zip = %s AND country = %s),%s,%s)'
	dealership_data = (address1, address2, city, ZIP, country, dealership_name, hours)
	execute_query(db_connection, dealership_query, dealership_data)
	return redirect('/')


@webapp.route('/addEmployee/<int:dealership_id>', methods=['POST'])
def add_employee(dealership_id):
	db_connection = connect_to_database();
	fname = request.form['fname']
	lname = request.form['lname']
	position = request.form['position']
	employee_query = 'INSERT INTO employees (dealership_id, f_name, l_name, position) VALUES (%s, %s, %s, %s)'
	employee_data = (dealership_id, fname, lname, position)
	execute_query(db_connection, employee_query, employee_data)
	return redirect('selectDealership/' + str(dealership_id))


@webapp.route('/addVehicle/<int:dealership_id>', methods=['POST'])
def add_vehicle(dealership_id):
	db_connection = connect_to_database();
	veh_type = request.form['type']
	vin = request.form['vin']

	#add type to table if new
	types_query = "INSERT IGNORE INTO vehicle_type (type_name) VALUES (%s)"
	types_data = (veh_type)
	execute_query(db_connection, types_query, [types_data])
	type_id_query = "SELECT type_id FROM vehicle_type WHERE type_name = %s"
	type_id = execute_query(db_connection, type_id_query, [types_data]).fetchone();

	vehicle_query = "INSERT INTO vehicle (dealership_id, type, vin) VALUES (%s, %s, %s)"
	vehicle_data = (dealership_id, type_id, vin)
	execute_query(db_connection, vehicle_query, vehicle_data)
	#add features to vehicle???
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

### UPDATE ROUTES

@webapp.route('/updateDealership/<int:dealership_id>', methods=['POST'])
def update_dealership(dealership_id):
	db_connection = connect_to_database();
	address1 = request.form['address1']
	address2 = request.form['address2']
	city = request.form['city']
	ZIP = request.form['ZIP']
	country = request.form['country']
	hours = request.form['hours']
	dealership_name = request.form['dealership_name']
	query = "UPDATE dealership, dealership_address SET dealership_name = %s, hours = %s, address_line_1 = %s, address_line_2 = %s, city = %s, zip = %s, country = %s WHERE dealership_id = %s AND dealership_address.address_id = (SELECT address_id FROM dealership WHERE dealership_id = %s)"
	data = (dealership_name, hours, address1, address2, city, ZIP, country, dealership_id, dealership_id)
	execute_query(db_connection, query, data)
	return redirect('/')

@webapp.route('/updateEmployee/<int:dealership_id>/<int:employee_id>', methods=['POST'])
def update_employee(dealership_id, employee_id):
	db_connection = connect_to_database();
	fname = request.form['fname']
	lname = request.form['lname']
	position = request.form['position']
	query = "UPDATE employees SET f_name = %s, l_name = %s, position = %s WHERE employee_id = %s"
	data = (fname, lname, position, employee_id)
	execute_query(db_connection, query, data)
	return redirect('selectDealership/' + str(dealership_id))

@webapp.route('/updateVehicle/<int:dealership_id>/<int:vehicle_id>', methods=['POST'])
def update_vehicle(dealership_id, vehicle_id):
	db_connection = connect_to_database();
	vehicle_type = request.form['type']
	vin = request.form['vin']
	#add type to table if new
	types_query = "INSERT IGNORE INTO vehicle_type (type_name) VALUES (%s)"
	types_data = (vehicle_type)
	execute_query(db_connection, types_query, [types_data])
	type_id_query = "SELECT type_id FROM vehicle_type WHERE type_name = %s"
	type_id = execute_query(db_connection, type_id_query, [types_data]).fetchone();

	query = "UPDATE vehicle SET type = %s, vin = %s WHERE vehicle_id = %s"
	data = (type_id, vin, vehicle_id)
	execute_query(db_connection, query, data)
	return redirect('selectDealership/' + str(dealership_id))

@webapp.route('/updateFeature/<int:dealership_id>/<int:vehicle_id>/<int:feature_id>', methods=['POST'])
def update_feature(dealership_id, vehicle_id, feature_id):
	db_connection = connect_to_database();
	value = request.form['value']
	query = "UPDATE vehicle_feature SET feature_value = %s WHERE vehicle_id = %s AND feature_id = %s"
	data = (value, vehicle_id, feature_id)
	execute_query(db_connection, query, data)
	return redirect('selectVehicle/' + str(dealership_id) + '/' + str(vehicle_id))
