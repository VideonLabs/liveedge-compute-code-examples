# Videon RESTful Python Helper Library

The `videon_restful.py` file is intended to be a simple Python library that sets up the communication between your Python code and the LiveEdge Compute APIs running on the EdgeCaster. 

## Usage

Place the `videon_restful.py` file in a directory accessible by your Python script - either a dedicated library subdirectory or the main directory alongside your application. Simply import it in your script and access it directly:

    import videon_restful
    result = videon_restful.get_system_properties('127.0.0.1')
