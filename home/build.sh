python -m grpc_tools.protoc \
  --proto_path=TypeMasterProto \
  --python_out=pb2 \
  --grpc_python_out=pb2 \
  TypeMasterProto/prompt.proto

python -m grpc_tools.protoc \
  --proto_path=TypeMasterProto \
  --python_out=pb2 \
  --grpc_python_out=pb2 \
  TypeMasterProto/scoring.proto

echo "✔ gRPC stubs generated in pb2/"
