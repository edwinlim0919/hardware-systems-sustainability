for i in geo profile rate recommend rsv search user
do
          IMAGE=hotel_reserv_${i}_single_node:latest
          sudo docker image tag $IMAGE localhost:7696/${IMAGE}
done

for i in frontend
do
          IMAGE=hotel_reserv_${i}_modified:latest
          sudo docker image tag $IMAGE localhost:7696/${IMAGE}
done

echo "Tagged image"
sudo docker image ls --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'

for i in geo profile rate recommend rsv search user
do
          IMAGE=hotel_reserv_${i}_single_node:latest
          sudo docker push localhost:7696/${IMAGE}
done

for i in frontend
do
          IMAGE=hotel_reserv_${i}_modified:latest
          sudo docker push localhost:7696/${IMAGE}
done

echo "Pushed images"
sudo docker image ls --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'
