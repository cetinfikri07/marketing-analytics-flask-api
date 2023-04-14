# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloud_sql_mysql_sqlalchemy_connect_unix]
from pathlib import Path
import sqlalchemy
import yaml
import os


basedir = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute())


def connect_unix_socket() -> sqlalchemy.engine.base.Engine:
    """ Initializes a Unix socket connection pool for a Cloud SQL instance of MySQL. """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    config_path = basedir+'/app.yaml'

    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    unix_socket_path = os.environ.get('INSTANCE_UNIX_SOCKET', config['env_variables']['INSTANCE_UNIX_SOCKET'])
    db_user = os.environ.get('DB_USER', config['env_variables']['DB_USER'])
    db_pass = os.environ.get('DB_PASS', config['env_variables']['DB_PASS'])
    db_name = os.environ.get('DB_NAME', config['env_variables']['DB_NAME'])

    creds = {
        "Username": db_user,
        "Password": db_pass,
        "Db name": db_name,
        "unix socket path": unix_socket_path
    }

    print(creds)

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_socket": unix_socket_path},
        ),
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,

        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,

        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.

        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds

        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool

# [END cloud_sql_mysql_sqlalchemy_connect_unix]
