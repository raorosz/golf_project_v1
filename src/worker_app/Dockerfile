# Use the official .NET Core SDK as a build image
FROM mcr.microsoft.com/dotnet/sdk:8.0.201 AS build
WORKDIR /app

# Copy the .csproj file and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy the remaining source code and build the application
COPY . ./
RUN dotnet publish -c Release -o out

# Use the official .NET Core runtime as the base image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Copy the built application from the build image
COPY --from=build /app/out ./

# Define the command to run the worker app
ENTRYPOINT ["dotnet", "Worker.dll"]