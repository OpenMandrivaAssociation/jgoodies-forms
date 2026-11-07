Name:		jgoodies-forms
Version:	1.9.0
Release:	1
Summary:	Framework to lay out and implement elegant Swing panels
Group:		Development/Java
License:	BSD
URL:		https://www.jgoodies.com/
# Upstream no longer publishes the vendor zip. This is the last open-source
# release, and the Maven Central sources jar is the source of record.
Source0:	https://repo1.maven.org/maven2/com/jgoodies/jgoodies-forms/1.9.0/jgoodies-forms-1.9.0-sources.jar#/jgoodies-forms-%{version}-sources.zip

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(com.jgoodies:jgoodies-common)
BuildSystem:	maven
BuildOption(install):	--file-name jgoodies-forms

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
JGoodies Forms lays out Swing panels on a grid of columns and rows.
1.9.0 is binary incompatible with 1.8.0: it adds the previously
closed-source FormBuilder, adds Padding and Paddings, and deprecates
PanelBuilder, I15dPanelBuilder, and DefaultFormBuilder.
The build uses the system jgoodies-common 1.8.1 jar.
The compiler source level is 1.8. Tests are skipped.

%prep
%autosetup -c -n jgoodies-forms-%{version}
python - <<'PY'
import shutil
from pathlib import Path

src = Path("src/main/java")
src.mkdir(parents=True)
shutil.move("com", src / "com")
meta = Path("META-INF")
if meta.exists():
    shutil.rmtree(meta)

java_files = list(src.rglob("*.java"))
if len(java_files) != 43:
    raise SystemExit("java files " + str(len(java_files)))
if list(Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")

header = Path("src/main/java/com/jgoodies/forms/layout/FormLayout.java").read_text(encoding="utf-8")
start = header.index("/*")
end = header.index("*/")
lines = []
for line in header[start + 2:end].splitlines():
    if line.startswith(" *"):
        line = line[2:]
        if line.startswith(" "):
            line = line[1:]
    lines.append(line.rstrip())
Path("LICENSE.txt").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
license_text = Path("LICENSE.txt").read_text(encoding="utf-8")
if "JGoodies Software GmbH" not in license_text or "AS IS" not in license_text:
    raise SystemExit("license text was not extracted")

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.jgoodies</groupId>
  <artifactId>jgoodies-forms</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>JGoodies Forms</name>
  <description>Swing form layout built against the system jgoodies-common jar.</description>
  <url>https://www.jgoodies.com/</url>
  <licenses>
    <license>
      <name>BSD</name>
      <url>https://www.jgoodies.com/</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.jgoodies</groupId>
      <artifactId>jgoodies-common</artifactId>
      <version>1.8.1</version>
    </dependency>
  </dependencies>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <source>1.8</source>
          <target>1.8</target>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>jgoodies-forms</artifactId>",
    "<artifactId>jgoodies-common</artifactId>",
    "<version>1.8.1</version>",
    "<version>%{version}</version>",
    "<source>1.8</source>",
    "<target>1.8</target>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "oss-parent", "<source>1.6</source>", "SNAPSHOT", "<release>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/jgoodies-forms-%{version}.jar --describe-module jgoodies.forms > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^jgoodies.forms' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE.txt overview.html
