
# In other server
- Display new conda env
    
    ```shell
    conda env create -f environment.yml 
    ```

- Update new env

    ```shell
    conda env update -f environment.yml
    ```

- 2 way for generating the requirements.txt

    ```shell
    pipreqs ./
    pip freeze > requirements.txt
    ```